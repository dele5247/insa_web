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

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            self.stdout.write(self.style.ERROR(f'CSV file "{csv_file}" does not exist'))
            return

        # Try opening the CSV file with different encodings
        encodings = ['utf-8', 'latin1', 'cp1252']
        for encoding in encodings:
            try:
                with open(csv_file_path, 'r', encoding='euc-kr', newline='') as file:
                    reader = csv.reader(file, delimiter=',')
                    headers = next(reader)  # Skip the header row
                    Department.objects.all().delete()  # Clear existing data
                    for row in reader:

                        obj = Department(
                            dept_id=row[0],
                            dept_name=row[1],
                            ou_name=row[2],
                            acct_tp=row[3],
                        )
                        obj.save()
                        print(f'Imported: {row[1]} ({row[0]})')
                self.stdout.write(self.style.SUCCESS(f'Data imported successfully using {encoding} encoding'))
                break
            except UnicodeDecodeError:
                self.stdout.write(self.style.WARNING(f'Failed to read CSV file with {encoding} encoding'))

