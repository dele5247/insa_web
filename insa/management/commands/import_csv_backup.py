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
            Employee.objects.all().delete()
            for index,row in enumerate(reader):
                if index < last_count-1:
                    # Assuming your CSV has columns 'field1', 'field2', 'field3'...
                    # Modify this part according to your CSV structure and Django model
                    obj = Employee(
                        employee_id=row[0],
                        employee_number=row[1],
                        employee_name=row[2],
                        chinese_name=row[3],
                        english_name=row[4],
                        employment_status=row[5],
                        personal_id=row[6],
                        hr_department=row[7],
                        salary_department=row[8],
                        work_department=row[9],
                        expense_department=row[10],
                        workshop_code=row[11],
                        position=row[12],
                        birthdate=row[13],
                        ssn=row[14],
                        domicile_addr=row[15],
                        zip_code=row[16],
                        addr1=row[17],
                        addr2=row[18],
                        tel_no=row[19],
                        enter_dt=row[20],
                        retire_dt=row[21],
                        annc_dt=row[22],
                        chan=row[23],
                        bsln=row[24],
                        dso_code=row[25],
                        insert_date=row[26],
                        insert_user=row[27],
                        employee_pk=row[28],
                        sex_tp=row[29],
                        jikwi_cd=row[30],
                        jikwi_nm=row[31],
                        jikchaek_cd=row[32],
                        jikchaek_nm=row[33],
                        jikup_cd=row[34],
                        jikup_nm=row[35],
                        persg=row[36],
                        persk=row[37],
                        auth=row[38],
                        # Add more fields as needed
                    )
                    obj.save()
                    print(row[0],row[1])
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
