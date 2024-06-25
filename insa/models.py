from django.db import models

class Employee(models.Model):
    id = models.AutoField(primary_key=True)  # 기본 키 추가
    employee_id = models.CharField(max_length=20,null=True)
    employee_number = models.CharField(max_length=20)
    employee_name = models.CharField(max_length=100)
    chinese_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=10)
    personal_id = models.CharField(max_length=20)
    hr_department = models.CharField(max_length=10)
    salary_department = models.CharField(max_length=10)
    work_department = models.CharField(max_length=10)
    expense_department = models.CharField(max_length=10)
    workshop_code = models.CharField(max_length=10)
    position = models.CharField(max_length=10)
    birthdate = models.CharField(max_length=10)
    ssn = models.CharField(max_length=20)
    domicile_addr = models.CharField(max_length=100,null=True)
    zip_code = models.CharField(max_length=100,null=True)
    addr1 = models.CharField(max_length=100,null=True)
    addr2 = models.CharField(max_length=100,null=True)
    tel_no = models.CharField(max_length=100,null=True)
    enter_dt = models.CharField(max_length=100,null=True)
    retire_dt = models.CharField(max_length=100,null=True)
    annc_dt = models.CharField(max_length=100,null=True)
    chan = models.CharField(max_length=100,null=True)
    bsln = models.CharField(max_length=100,null=True)
    dso_code = models.CharField(max_length=100,null=True)
    insert_date = models.CharField(max_length=100,null=True)
    insert_user = models.CharField(max_length=100,null=True)
    employee_pk = models.CharField(max_length=100,null=True)
    sex_tp = models.CharField(max_length=100,null=True)
    jikwi_cd = models.CharField(max_length=100,null=True)
    jikwi_nm = models.CharField(max_length=100,null=True)
    jikchaek_cd = models.CharField(max_length=100,null=True)
    jikchaek_nm = models.CharField(max_length=100,null=True)
    jikup_cd = models.CharField(max_length=100,null=True)
    jikup_nm = models.CharField(max_length=100,null=True)
    persg = models.CharField(max_length=100,null=True)
    persk = models.CharField(max_length=100,null=True)
    auth = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.employee_name


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    dept_id = models.CharField(max_length=255, null=True)
    dept_code = models.IntegerField()
    dept_name = models.CharField(max_length=255)
    dept_abrv = models.CharField(max_length=255)
    mana_tp = models.CharField(max_length=255, blank=True, null=True)
    tax_biz = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    addr1 = models.CharField(max_length=255, blank=True, null=True)
    addr2 = models.CharField(max_length=255, blank=True, null=True)
    priox = models.CharField(max_length=255, blank=True, null=True)
    dept_stat = models.CharField(max_length=255, blank=True, null=True)
    up_dept_code = models.CharField(max_length=255, blank=True, null=True)
    sum_dept_code = models.CharField(max_length=255, blank=True, null=True)
    cur_dept_code = models.CharField(max_length=255, blank=True, null=True)
    buseo_tp = models.CharField(max_length=255, blank=True, null=True)
    dso_code = models.CharField(max_length=255, blank=True, null=True)
    org_cd = models.CharField(max_length=255, blank=True, null=True)
    insert_date = models.CharField(max_length=255)
    insert_user = models.CharField(max_length=255, blank=True, null=True)
    update_date = models.CharField(max_length=255)
    update_user = models.CharField(max_length=255, blank=True, null=True)
    acct_tp = models.CharField(max_length=255, blank=True, null=True)
    st_tp = models.CharField(max_length=255, blank=True, null=True)
    st_nm = models.CharField(max_length=255, blank=True, null=True)
    begda = models.CharField(max_length=255)
    endda = models.CharField(max_length=255)


class Setting(models.Model):
    site_name = models.CharField(max_length=100)
    admin_email = models.EmailField()
    ad_server = models.CharField(max_length=255, null=True)
    ad_user = models.CharField(max_length=255, null=True)
    ad_password = models.CharField(max_length=255, null=True)
    base_dn = models.CharField(max_length=255, null=True)
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

