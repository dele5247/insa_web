from django.db import models

class Employee(models.Model):
    id = models.AutoField(primary_key=True)  # 기본 키 추가
    employee_id = models.CharField(max_length=20, null=True)  # employeeID
    sAMAccountName = models.CharField(max_length=100, null=True)  # cn,name,sAMAccountName
    upn = models.CharField(max_length=100, null=True)  # UPN
    display_name = models.CharField(max_length=100, null=True)  # displayName
    last_name = models.CharField(max_length=100, null=True)  # sn
    first_name = models.CharField(max_length=100, null=True)  # givenName
    description = models.CharField(max_length=100, null=True)  # description(최초 1회)
    title = models.CharField(max_length=100, null=True)  # title
    department = models.CharField(max_length=100, null=True)  # department
    company = models.CharField(max_length=100, null=True)  # company
    email = models.CharField(max_length=100, null=True)  # mail
    employment_status = models.CharField(max_length=20, null=True)  # 재직여부
    group = models.CharField(max_length=100, null=True)  # group
    create_date = models.DateTimeField('Create Date', auto_now_add=True, null=True)

    def __str__(self):
        return self.display_name or self.first_name or self.employee_id


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    dept_id = models.CharField(max_length=255, null=True)
    dept_name = models.CharField(max_length=255)
    ou_name = models.CharField(max_length=255)
    update_user = models.CharField(max_length=255, blank=True, null=True)
    acct_tp = models.CharField(max_length=255, blank=True, null=True)
    create_date = models.DateTimeField('Create Date', auto_now_add=True, null=True)


class Setting(models.Model):
    site_name = models.CharField(max_length=100)
    admin_email = models.EmailField()
    ad_server = models.CharField(max_length=255, null=True)
    ad_user = models.CharField(max_length=255, null=True)
    ad_password = models.CharField(max_length=255, null=True)
    base_dn = models.CharField(max_length=255, null=True)
    root_dn = models.CharField(max_length=255, null=True)
    ftp_host = models.CharField(max_length=255, null=True)
    ftp_username = models.CharField(max_length=255, null=True)
    ftp_password = models.CharField(max_length=255, null=True)
    ftp_remote_path = models.CharField(max_length=255, null=True)
    ftp_path = models.CharField(max_length=255, null=True)
    license_key = models.CharField(max_length=255, null=True)
    def __str__(self):
        return self.site_name


class Log(models.Model):
    no = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, null=True)
    desc = models.CharField(max_length=255, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)

class Schedule(models.Model):
    csv_path = models.CharField(max_length=255)
    group_csv_path = models.CharField(max_length=255,null=True)
    hour = models.IntegerField()
    minute = models.IntegerField()

    def __str__(self):
        return f'{self.csv_path} - {self.hour}:{self.minute}'

