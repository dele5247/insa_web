import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand
#from django_extensions.db.models import Employee, Department 
from insa.models import Employee, Department, Setting


class Command(BaseCommand):
    help = 'Import data from DB and add users to AD server'

    def add_arguments(self, parser):
        parser.add_argument('ad_server', type=str, help='AD server address')
        parser.add_argument('ad_user', type=str, help='AD admin username')
        parser.add_argument('ad_password', type=str, help='AD admin password')
        parser.add_argument('base_dn', type=str, help='Base DN for AD entries')

    def handle(self, *args, **kwargs):
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
            user_dn = f"CN={employee.emp_name},{base_dn}"
            attributes = {
                'givenName': employee.emp_name,
                'sn': employee.emp_name,
                'employeeID': employee.emp_no,
                'userPrincipalName': f"{employee.emp_eng_name}@example.com",  # Adjust domain as needed
                'sAMAccountName': employee.emp_eng_name,
                'objectClass': ['top', 'person', 'organizationalPerson', 'user']
            }

            try:
                conn.add(user_dn, attributes=attributes)
                if conn.result['description'] == 'success':
                    self.stdout.write(self.style.SUCCESS(f'Successfully added {employee.emp_name} to AD'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to add {employee.emp_name} to AD: {conn.result}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding {employee.emp_name} to AD: {str(e)}'))

        conn.unbind()

