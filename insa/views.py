from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Department, Setting, Log
from .forms import EmployeeForm, DepartmentForm, SettingForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count
import datetime
import base64

sets=Setting.objects.all()
setting = Setting.objects.get(site_name='AD_SETTINGS')

@login_required
def index(request):
    # Employee 데이터를 집계하여 차트 데이터로 변환
    department_counts = Employee.objects.values('work_department').annotate(count=Count('id')).order_by('work_department')

    departments = list(department_counts.values_list('work_department', flat=True))
    counts = list(department_counts.values_list('count', flat=True))

    context = {
        'departments': departments,
        'counts': counts,
        'sets': sets,
        'license_expiry_date': check_license(),

    }
    return render(request, 'index.html', context)

@login_required
def input_page(request):
    return render(request, 'input_page.html', {'sets': sets, 'license_expiry_date': check_license()})


@login_required
def table_page(request):
    data = Employee.objects.all()
    return render(request, 'table_page.html', {'data': data, 'sets': sets, 'license_expiry_date': check_license()})

def employee_form(request, id=None):
    if id:
        employee = get_object_or_404(Employee, id=id)
    else:
        employee = None

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('table_page')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employee_form.html', {'form': form, 'sets': sets, 'license_expiry_date': check_license()})


@login_required
def log_table_page(request):
    data = Log.objects.all()
    return render(request, 'log_table_page.html', {'data': data, 'sets': sets, 'license_expiry_date': check_license()})



@login_required
def department_table_page(request):
    data = Department.objects.all()
    return render(request, 'department_table_page.html', {'data': data, 'sets': sets, 'license_expiry_date': check_license()})

def department_form(request, id=None):
    if id:
        department = get_object_or_404(Department, id=id)
    else:
        department = None

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_table_page')
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'department_form.html', {'form': form, 'sets': sets, 'license_expiry_date': check_license()})

def settings(request):
    setting = Setting.objects.first()
    if not setting:
        setting = Setting.objects.create(site_name='Default Site', admin_email='admin@example.com')
    if request.method == 'POST':
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('settings')
    else:
        form = SettingForm(instance=setting)
    return render(request, 'settings.html', {'form': form, 'sets': sets, 'license_expiry_date': check_license()})

def lockscreen(request):
    setting = Setting.objects.first()
    if not setting:
        setting = Setting.objects.create(site_name='Default Site', admin_email='admin@example.com')
    if request.method == 'POST':
        license_key = request.POST.get('license_key')
        setting.license_key = license_key
        setting.save()
        print(setting.license_key)
        return redirect('index')
    return render(request, 'lockscreen.html')


def set_license_expiry(request):
    if request.method == 'POST':
        form = LicenseForm(request.POST)
        if form.is_valid():
            license_expiry_date = form.cleaned_data['license_expiry_date']
            settings.LICENSE_EXPIRY_DATE = license_expiry_date.strftime('%Y-%m-%d')
            return redirect('home')  # 설정을 업데이트한 후 리디렉션
    else:
        form = LicenseForm()
    return render(request, 'license_form.html', {'form': form, 'license_expiry_date': check_license()})

def check_license():
    setting = Setting.objects.get(site_name='AD_SETTINGS')
    license_key = setting.license_key
    shift=3
    try:
        base64_bytes = license_key.encode('utf-8')
        encrypted_date_bytes = base64.b64decode(base64_bytes)
        encrypted_date = encrypted_date_bytes.decode('utf-8')

        parts = encrypted_date.split('-')
        decrypted_date = ''
        for part in parts:
            decrypted_part = ''
            for char in part:
                decrypted_part += chr((ord(char) - ord('0') - shift) % 10 + ord('0'))
            decrypted_date += decrypted_part + '-'

        decrypted_date = decrypted_date.rstrip('-')
        expiry_date = datetime.datetime.strptime(decrypted_date, '%Y-%m-%d').date()
        return "라이센스 기간 : " + str(expiry_date)
    except:
        return "유효한 라이센스가 아니거나 잘못된 키입니다."
