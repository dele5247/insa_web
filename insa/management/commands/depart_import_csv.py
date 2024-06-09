import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand
#from django_extensions.db.models import Employee, Department 
from insa.models import Employee, Department 


class Command(BaseCommand):
    help = 'Import data from CSV file to SQLite database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        csv_file_path = os.path.join(settings.BASE_DIR, csv_file)

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file "{csv_file}" does not exist'))
            return

        # Open the CSV file and iterate over its rows
        with open(csv_file_path, 'r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file, delimiter=',')
            last_count=len(list(reader))
            file.seek(0)
            Department.objects.all().delete()
            for index,row in enumerate(reader):
                if index < last_count-1:
                    # Assuming your CSV has columns 'field1', 'field2', 'field3'...
                    # Modify this part according to your CSV structure and Django model
                    obj = Department(
                        dept_id=row[0],
                        dept_code=row[1],
                        dept_name=row[2],
                        dept_abrv=row[3],
                        mana_tp=row[4],
                        tax_biz=row[5],
                        zip_code=row[6],
                        addr1=row[7],
                        addr2=row[8],
                        priox=row[9],
                        dept_stat=row[10],
                        up_dept_code=row[11],
                        sum_dept_code=row[12],
                        cur_dept_code=row[13],
                        buseo_tp=row[14],
                        dso_code=row[15],
                        org_cd=row[16],
                        insert_date=row[17],
                        insert_user=row[18],
                        update_date=row[19],
                        update_user=row[20],
                        acct_tp=row[21],
                        st_tp=row[22],
                        st_nm=row[23],
                        begda=row[24],
                        endda=row[25],
                        # Add more fields as needed
                    )
                    obj.save()
                    print(row[0],row[1])
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
