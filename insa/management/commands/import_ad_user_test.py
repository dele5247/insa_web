import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from insa.models import Employee, Department, Setting
import ldap3
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE

def create_ou_if_not_exists(conn, ou_dn, base_dn):
    """
    Create an OU if it does not exist. Create parent OUs recursively.
    """
    base_count = base_dn.count(',')
    ou_parts = ou_dn.split(',')
    ou_parts.reverse()  # OU를 역순으로 조정하여 가장 하위 OU부터 처리
    for i in range(len(ou_parts)):
        if i > base_count:
            current_ou_dn = ','.join(reversed(ou_parts[:i+1]))  # 현재 OU DN을 생성하고
            try:
                conn.search(current_ou_dn, f'(objectClass=organizationalUnit)')
            except:
                pass
            if not conn.entries:
                ou_name = ou_parts[i].split('=')[1]  # OU 이름을 추출하고
                if ou_name == "99999":  # 최상위 OU는 건너뜁니다.
                    continue
                parent_ou_dn = ','.join(reversed(ou_parts[i + 1:]))  # 상위 OU DN을 생성한 후
                if parent_ou_dn:  # 상위 OU가 있다면
                    parent_ou_dn = ','.join(reversed(parent_ou_dn.split(',')[1:]))  # 역순으로 조합합니다.
                conn.add(current_ou_dn, 'organizationalUnit', {'ou': ou_name})  # OU를 추가합니다.
                if conn.result['description'] == 'success':
                    print(f'Successfully created OU: {ou_name} at {current_ou_dn}')
                else:
                    print(f'Failed to create OU: {ou_name} at {current_ou_dn}: {conn.result}')
                    return False
    return True

def create_group_if_not_exists(conn, group_name, ou_dn):
    """
    Create a security group if it does not exist in the given OU and add users in the OU to the group.
    """
    group_dn = f"CN={group_name},{ou_dn}"
    conn.search(group_dn, '(objectClass=group)')
    if not conn.entries:
        conn.add(group_dn, 'group', {
            'sAMAccountName': group_name,
            'groupType': -2147483646,  # Security group
            'description': f'Security group for {group_name}'
        })
        if conn.result['description'] == 'success':
            print(f'Successfully created group: {group_name} at {group_dn}')
            add_users_to_group(conn, ou_dn, group_dn)
        else:
            print(f'Failed to create group: {group_name} at {group_dn}: {conn.result}')
    else:
        add_users_to_group(conn, ou_dn, group_dn)

def add_users_to_group(conn, ou_dn, group_dn):
    """
    Add all users in the given OU to the specified group if they are not already members.
    """
    conn.search(ou_dn, '(objectClass=user)', attributes=['distinguishedName'])
    user_dns = [entry.distinguishedName.value for entry in conn.entries]

    for user_dn in user_dns:
        # Check if the user is already a member of the group
        conn.search(group_dn, '(member={user_dn})', attributes=['member'])
        if not conn.entries:
            # User is not a member of the group, add them
            conn.modify(group_dn, {'member': [(MODIFY_ADD, [user_dn])]})
            if conn.result['description'] == 'success':
                print(f'Successfully added {user_dn} to group: {group_dn}')
            else:
                pass
                #print(f'Failed to add {user_dn} to group: {group_dn}: {conn.result}')

def remove_user_from_other_groups(conn, base_dn,user_dn, current_group_dn):
    """
    Remove the user from all other groups except the current one.
    """
    conn.search(base_dn, f'(member={user_dn})', attributes=['distinguishedName'])
    group_dns = [entry.distinguishedName.value for entry in conn.entries if entry.distinguishedName.value != current_group_dn]

    for group_dn in group_dns:
        print(user_dn, group_dn)
        conn.modify(group_dn, {'member': [(MODIFY_DELETE, [user_dn])]})
        if conn.result['description'] == 'success':
            print(f'Successfully removed {user_dn} from group: {group_dn}')
        else:
            #print(f'Failed to remove {user_dn} from group: {group_dn}: {conn.result}')
            pass


def build_ou_dn(department, base_dn):
    """
    Build the OU DN for the given department, including parent OUs.
    """
    ou_parts = []
    while department:
        ou_parts.insert(0, f"OU={department.dept_name}")
        if department.acct_tp:
            try:
                if department.acct_tp == "0" or department.acct_tp == "00000000" or department.acct_tp == "99999" or department.acct_tp == "00099999":
                    department = None
                else:
                    department = Department.objects.get(dept_id=department.acct_tp)
            except Department.DoesNotExist:
                print(f"Parent department with dept_id {department.acct_tp} does not exist.")
                department = None
        else:
            department = None
    ou_parts.reverse()  # OU를 역순으로 변경하여 추가된 OU가 먼저 오도록 함
    ou_dn = ','.join(ou_parts) + ',' + base_dn
    return ou_dn

class Command(BaseCommand):
    help = 'Import data from DB and add/update users to AD server'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=str, help='user id')

    def handle(self, *args, **kwargs):
        # Setting 모델에서 AD 서버 정보를 가져옴
        ad_settings = Setting.objects.get(site_name='AD_SETTINGS')
        ad_server = ad_settings.ad_server
        ad_user = ad_settings.ad_user
        ad_password = ad_settings.ad_password
        base_dn = ad_settings.base_dn
        root_dn = ad_settings.root_dn

        server = Server(ad_server, get_info=ALL)
        conn = Connection(server, user=ad_user, password=ad_password, auto_bind=True)

        # Get all employees from the database
        employees = Employee.objects.filter(sAMAccountName=kwargs['user_id'])

        for employee in employees:
            # Get the department information
            try:
                department = Department.objects.get(dept_id=employee.group)
            except Department.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Department with dept_id {employee.group} does not exist for employee {employee.display_name}. Skipping...'))
                continue

            ou_dn = build_ou_dn(department, base_dn)
            # Create the OU if it does not exist
            if not create_ou_if_not_exists(conn, ou_dn, base_dn):
                self.stdout.write(self.style.ERROR(f'Failed to create the OU structure for {employee.display_name}. Skipping...'))
                continue

            user_dn = f"CN={employee.sAMAccountName},{ou_dn}"
            attributes = {
                'givenName': employee.first_name,
                'sn': employee.last_name,
                'displayName': employee.display_name,
                'description': employee.description,
                'employeeID': employee.employee_id,
                'userPrincipalName': employee.upn,  # Adjust domain as needed
                'mail': employee.email or employee.upn,
                'sAMAccountName': employee.sAMAccountName,
                'userAccountControl': '544',  # 544 is for normal account, enable account
                'objectClass': ['top', 'person', 'organizationalPerson', 'user']
            }

            # Check if the user already exists in AD
            conn.search(root_dn, f'(sAMAccountName={employee.sAMAccountName})', attributes=['distinguishedName'])
            if conn.entries:
                current_user_dn = conn.entries[0].distinguishedName.value
                current_ou = ','.join(current_user_dn.split(',')[1:])

                if current_ou != ou_dn:
                    # User exists but is in the wrong OU, move the user
                    self.stdout.write(self.style.SUCCESS(f'User {employee.sAMAccountName} exists but in the wrong OU. Moving...'))
                    try:
                        conn.modify_dn(current_user_dn, f"CN={employee.sAMAccountName}", new_superior=ou_dn)
                        conn.search(root_dn, f'(sAMAccountName={employee.sAMAccountName})', attributes=['distinguishedName'])
                        current_user_dn = conn.entries[0].distinguishedName.value
                        if conn.result['description'] == 'success':
                            self.stdout.write(self.style.SUCCESS(f'Successfully moved {employee.sAMAccountName} to the correct OU'))
                        else:
                            self.stdout.write(self.style.ERROR(f'Failed to move {employee.sAMAccountName} to the correct OU: {conn.result}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error moving {employee.sAMAccountName} to the correct OU: {str(e)}'))

                # Update user attributes if necessary
                self.stdout.write(self.style.SUCCESS(f'Updating attributes for {employee.sAMAccountName}...'))
                try:
                    conn.modify(current_user_dn, {
                        'givenName': [(MODIFY_REPLACE, [employee.first_name])],
                        'sn': [(MODIFY_REPLACE, [employee.last_name])],
                        'displayName': [(MODIFY_REPLACE, [employee.display_name])],
                        'employeeID': [(MODIFY_REPLACE, [employee.employee_id])],
                        'userPrincipalName': [(MODIFY_REPLACE, [employee.upn])],
                        'mail': [(MODIFY_REPLACE, [employee.email or employee.upn])],
                        'sAMAccountName': [(MODIFY_REPLACE, [employee.sAMAccountName])]
                    })
                    if conn.result['description'] == 'success':
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated {employee.sAMAccountName} in AD'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to update {employee.sAMAccountName} in AD: {conn.result}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating {employee.sAMAccountName} in AD: {str(e)}'))
            else:
                # User does not exist, add the user
                self.stdout.write(self.style.SUCCESS(f'User {employee.sAMAccountName} does not exist. Adding...'))
                try:
                    conn.add(user_dn, attributes=attributes)
                    if conn.result['description'] == 'success':
                        self.stdout.write(self.style.SUCCESS(f'Successfully added {employee.sAMAccountName} to AD'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to add {employee.sAMAccountName} to AD: {conn.result}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error adding {employee.sAMAccountName} to AD: {str(e)}'))

            # Create the security group if it does not exist and add the user to the group
            create_group_if_not_exists(conn, department.dept_name, ou_dn)
            # Remove user from other groups if necessary
            try:
                remove_user_from_other_groups(conn, base_dn,user_dn, f"CN={department.dept_name},{ou_dn}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error removing {department.dept_name} to AD: {str(e)}'))


        conn.unbind()

