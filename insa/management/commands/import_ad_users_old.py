import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand
#from django_extensions.db.models import Employee, Department
from insa.models import Employee, Department, Setting
import ldap3
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE

# Define a default password (change this to your desired default password)
DEFAULT_PASSWORD = "P!ssw0rd12QWZX"

def create_ou_if_not_exists(conn, ou_dn, base_dn):
    """
    Create an OU if it does not exist. Create parent OUs recursively.
    """
    base_count=base_dn.count(',')
    ou_parts = ou_dn.split(',')
    ou_parts.reverse()  # Reverse the OU parts to process from the bottom-most OU
    for i in range(len(ou_parts)):
        if i > base_count:
            current_ou_dn = ','.join(reversed(ou_parts[:i+1]))
            try:
                conn.search(current_ou_dn, f'(objectClass=organizationalUnit)')
            except:
                pass
            if not conn.entries:
                ou_name = ou_parts[i].split('=')[1]
                if ou_name == "99999":  # Skip the top-level OU
                    continue
                parent_ou_dn = ','.join(reversed(ou_parts[i + 1:]))
                if parent_ou_dn:
                    parent_ou_dn = ','.join(reversed(parent_ou_dn.split(',')[1:]))
                conn.add(current_ou_dn, 'organizationalUnit', {'ou': ou_name})
                if conn.result['description'] == 'success':
                    print(f'Successfully created OU: {ou_name} at {current_ou_dn}')
                else:
                    print(f'Failed to create OU: {ou_name} at {current_ou_dn}: {conn.result}')
                    return False
    return True


def build_ou_dn(department, base_dn):
    """
    Build the OU DN for the given department, including parent OUs
    """
    ou_parts = []
    while department:
        ou_parts.insert(0, f"OU={department.dept_name}")
        if department.up_dept_code:
            try:
                if department.up_dept_code == "0" or department.up_dept_code == "99999":
                    department = None
                else:
                    department = Department.objects.get(dept_code=department.up_dept_code)
            except Department.DoesNotExist:
                print(f"Parent department with dept_code {department.up_dept_code} does not exist.")
                department = None
        else:
            department = None
    ou_parts.reverse()  # Reverse OU parts so that added OU comes first
    ou_dn = ','.join(ou_parts) + ',' + base_dn
    return ou_dn

class Command(BaseCommand):
    help = 'Import data from DB and add/update users to AD server'

    def handle(self, *args, **kwargs):
        # Get AD server settings from the database
        ad_settings = Setting.objects.get(site_name='AD_SETTINGS')
        ad_server = ad_settings.ad_server
        ad_user = ad_settings.ad_user
        ad_password = ad_settings.ad_password
        base_dn = ad_settings.base_dn

        server = Server(ad_server, get_info=ALL)
        conn = Connection(server, user=ad_user, password=ad_password, auto_bind=True)

        # Get all employees from the database
        employees = Employee.objects.all()

        for employee in employees:
            try:
                department = Department.objects.get(dept_code=employee.hr_department)
            except Department.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Department with dept_code {employee.hr_department} does not exist for employee {employee.employee_name}. Skipping...'))
                continue

            ou_dn = build_ou_dn(department, base_dn)
            if not create_ou_if_not_exists(conn, ou_dn, base_dn):
                self.stdout.write(self.style.ERROR(f'Failed to create the OU structure for {employee.employee_name}. Skipping...'))
                continue

            user_dn = f"CN={employee.employee_name},{ou_dn}"

            # Convert password to UTF-16LE byte string and format for Active Directory
            #unicode_pwd = ('"' + DEFAULT_PASSWORD + '"').encode('utf-16-le')
            unicode_pwd = DEFAULT_PASSWORD.encode('utf-16-le')
            attributes = {
                'givenName': employee.employee_name,
                'sn': employee.employee_name,
                'displayName': employee.employee_name,
                'employeeID': employee.employee_id,
                'userPrincipalName': f"{employee.employee_number}@example.com",
                'sAMAccountName': employee.employee_number,
                'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
                'userAccountControl': '544',  # 512 is for normal account, enable account
                #'unicodePwd': unicode_pwd  # Set the default password (formatted for AD)
            }

            # Check if the user already exists in AD
            conn.search(base_dn, f'(sAMAccountName={employee.employee_number})', attributes=['sAMAccountName'])
            if conn.entries:
                # User exists, update the user
                #self.stdout.write(self.style.SUCCESS(f'User {employee.employee_name} exists. Updating...'))
                try:
                    conn.modify(user_dn, {
                        'givenName': [(MODIFY_REPLACE, [employee.employee_name])],
                        'sn': [(MODIFY_REPLACE, [employee.employee_name])],
                        'displayName': [(MODIFY_REPLACE, [employee.employee_name])],
                        'employeeID': [(MODIFY_REPLACE, [employee.employee_id])],
                        'userPrincipalName': [(MODIFY_REPLACE, [f"{employee.employee_number}@example.com"])],
                        'sAMAccountName': [(MODIFY_REPLACE, [employee.employee_number])]
                    })
                    if conn.result['description'] == 'success':
                        pass
                        #self.stdout.write(self.style.SUCCESS(f'Successfully updated {employee.employee_name} in AD'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to update {employee.employee_name} in AD: {conn.result}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating {employee.employee_name} in AD: {str(e)}'))
            else:
                # User does not exist, add the user
                self.stdout.write(self.style.SUCCESS(f'User {employee.employee_name} does not exist. Adding...'))
                try:
                    conn.add(user_dn, attributes=attributes)
                    if conn.result['description'] == 'success':
                        self.stdout.write(self.style.SUCCESS(f'Successfully added {employee.employee_name} to AD'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to add {employee.employee_name} to AD: {conn.result}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error adding {employee.employee_name} to AD: {str(e)}'))

        conn.unbind()
