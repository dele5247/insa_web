import os
import ftplib
from django.core.management.base import BaseCommand
from django.conf import settings
from insa.models import Employee, Department, Setting
import datetime

class Command(BaseCommand):
    help = 'Connect to FTP server and copy specified files to local directory'
    def handle(self, *args, **kwargs):

        ftp_settings = Setting.objects.get(site_name='AD_SETTINGS')
        ftp_server = ftp_settings.ftp_host
        ftp_user = ftp_settings.ftp_username
        ftp_password = ftp_settings.ftp_password
        remote_files = ftp_settings.ftp_remote_path.split(',')
        ad_server = ftp_settings.ad_server
        local_directory = ftp_settings.ftp_path
        print(ad_server,ftp_server,ftp_user,ftp_password,remote_files,local_directory)
        # Connect to the FTP server
        try:
            ftp = ftplib.FTP(ftp_server)
            ftp.login(user=ftp_user, passwd=ftp_password)
            self.stdout.write(self.style.SUCCESS(f'Successfully connected to FTP server {ftp_server}'))
        except ftplib.all_errors as e:
            self.stdout.write(self.style.ERROR(f'Failed to connect to FTP server: {str(e)}'))
            return

        # Ensure local directory exists
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

        # Download specified files
        for remote_file in remote_files:
            today_date = datetime.datetime.now()
            if "%Y" in remote_file and "%m" in remote_file and "%d" in remote_file:
                remote_file = today_date.strftime(remote_file)
            else:
               # 포함되어 있지 않으면 원래 경로 사용
                remote_file = remote_file
            local_filepath = os.path.join(local_directory, os.path.basename(remote_file))
            try:
                with open(local_filepath, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {remote_file}', local_file.write)
                self.stdout.write(self.style.SUCCESS(f'Successfully downloaded {remote_file} to {local_filepath}'))
            except ftplib.error_perm as e:
                self.stdout.write(self.style.ERROR(f'Failed to download {remote_file}: {str(e)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error saving {remote_file}: {str(e)}'))

        # Close the FTP connection
        ftp.quit()
