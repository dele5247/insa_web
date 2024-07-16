from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Department, Setting, Log, Schedule
from .forms import EmployeeForm, DepartmentForm, SettingForm
from django.contrib.auth.decorators import login_required
from django.conf import settings as django_settings
from django.db.models import Count
from django.db import connection, transaction
import threading
import datetime
import base64
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.core.management import call_command
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import logging
from django.core.cache import cache
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


# 전역 변수로 스케줄러 초기화
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
register_events(scheduler)
scheduler.start()

executing = False

@login_required
def index(request):
    # 직원 통계
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status='재직').count()
    total_department = Department.objects.all().count()

    # 부서별 직원 수
    department_counts = Employee.objects.values('group').annotate(count=Count('id'))
    departments = Employee.objects.values('department').annotate(total=Count('id')).order_by('-total')

    # 차트 데이터를 생성
    labels = [dept['department'] for dept in departments]
    data = [dept['total'] for dept in departments]

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_department': total_department,
        'department_counts': department_counts,
        'labels': labels,
        'data': data,
        'license_expiry_date': check_license(),
    }
    return render(request, 'index.html', context)


    ## Employee 데이터를 집계하여 차트 데이터로 변환
    #department_counts = Employee.objects.values('work_department').annotate(count=Count('id')).order_by('work_department')

    #departments = list(department_counts.values_list('work_department', flat=True))
    #counts = list(department_counts.values_list('count', flat=True))
    #context = {
    #    'departments': departments,
    #    'counts': counts,
    #    'sets': get_settings(),
    #    'license_expiry_date': check_license(),
    #}
    #return render(request, 'index.html', context)

@login_required
def input_page(request):
    return render(request, 'input_page.html', {'sets': get_settings(), 'license_expiry_date': check_license()})

@login_required
def table_page(request):
    cache_key = 'employee_list'
    cache_time = 600  # 시간(초) 단위로 캐시 유지 시간 설정
    data = cache.get(cache_key)
    if not data:
        data = Employee.objects.all()
    schedule = Schedule.objects.first()
    jobs = scheduler.get_jobs()
    return render(request, 'table_page.html', {'data': data, 'sets': get_settings(), 'schedule': schedule, 'jobs': jobs,'license_expiry_date': check_license()})

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

    return render(request, 'employee_form.html', {'form': form, 'sets': get_settings(), 'license_expiry_date': check_license()})

@login_required
def log_table_page(request):
    data = Log.objects.all().order_by('-no')
    return render(request, 'log_table_page.html', {'data': data, 'sets': get_settings(), 'license_expiry_date': check_license()})

@login_required
def department_table_page(request):
    cache_key = 'department_list'
    cache_time = 600  # 시간(초) 단위로 캐시 유지 시간 설정
    data = cache.get(cache_key)
    if not data:
        data = Department.objects.all()
    schedule = Schedule.objects.first()
    return render(request, 'department_table_page.html', {'data': data, 'sets': get_settings(), 'schedule': schedule, 'license_expiry_date': check_license()})

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

    return render(request, 'department_form.html', {'form': form, 'sets': get_settings(), 'license_expiry_date': check_license()})

def settings_view(request):
    setting = Setting.objects.filter(site_name='AD_SETTINGS').first()
    if not setting:
        setting = Setting.objects.create(site_name='AD_SETTINGS', admin_email='admin@example.com')
    if request.method == 'POST':
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('settings_view')
    else:
        form = SettingForm(instance=setting)
    return render(request, 'settings.html', {'form': form, 'sets': get_settings(), 'license_expiry_date': check_license()})

def lockscreen(request):
    setting = Setting.objects.filter(site_name='AD_SETTINGS').first()
    if not setting:
        setting = Setting.objects.create(site_name='AD_SETTINGS', admin_email='admin@example.com')
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
            django_settings.LICENSE_EXPIRY_DATE = license_expiry_date.strftime('%Y-%m-%d')
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

def get_settings():
    try:
        return Setting.objects.get(site_name='AD_SETTINGS')
    except Setting.DoesNotExist:
        setting = Setting.objects.create(site_name='AD_SETTINGS', admin_email='admin@example.com')
        return None

def log_schedule_activity(title, description):
    with transaction.atomic():
        Log.objects.create(title=title, desc=description)

def execute_import_csv(csv_path,group_csv_path):
    global executing
    if executing:
        return

    executing = True

    print("############# ftp sync Start ###############")
    try:
        call_command('ftp_file_sync')
        log_schedule_activity('File Sync Successful', f'Fie Sync completed successfully.')
    except Exception as e:
        log_schedule_activity('File Sync Failed', f'File Sync failed with error: {str(e)}')
    finally:
        executing = False

    print("############# import_csv Start ###############")
    try:
        call_command('import_csv', csv_path)
        log_schedule_activity('CSV Import Successful', f'CSV import for {csv_path} completed successfully.')
    except Exception as e:
        log_schedule_activity('CSV Import Failed', f'CSV import for {csv_path} failed with error: {str(e)}')
    finally:
        executing = False
        # 데이터베이스 연결 닫기
        connection.close()

    print("############# import_group_csv Start ###############")
    try:
        call_command('import_group_csv', group_csv_path)
        log_schedule_activity('CSV Import Successful', f'CSV import for {group_csv_path} completed successfully.')
    except Exception as e:
        log_schedule_activity('CSV Import Failed', f'CSV import for {group_csv_path} failed with error: {str(e)}')
    finally:
        executing = False
        # 데이터베이스 연결 닫기
        connection.close()
    
    print("############# import_ad_users Start ###############")
    try:
        call_command('import_ad_users')
        log_schedule_activity('AD Sync', f'AD Sync completed successfully.')
    except Exception as e:
        log_schedule_activity('AD Sync', f'AD Sync failed with error: {str(e)}')
    finally:
        executing = False



def run_import_csv_thread(csv_path,group_csv_path):
    thread = threading.Thread(target=execute_import_csv, args=(csv_path,group_csv_path))
    thread.start()


def schedule_import_csv(request):
    schedule = Schedule.objects.first()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'schedule':

            csv_path = request.POST.get('csv_path')
            group_csv_path = request.POST.get('group_csv_path')
            hour = request.POST.get('hour')
            minute = request.POST.get('minute')

            if not csv_path or not hour or not minute:
                return HttpResponseBadRequest('All fields are required')

            # 기존 스케줄 삭제
            scheduler.remove_all_jobs()

            # 새로운 스케줄 저장
            with transaction.atomic():
                if schedule:
                    schedule.csv_path = csv_path
                    schedule.group_csv_path = group_csv_path
                    schedule.hour = hour
                    schedule.minute = minute
                    schedule.save()
                else:
                    schedule = Schedule.objects.create(
                        csv_path=csv_path,
                        group_csv_path=group_csv_path,
                        hour=hour,
                        minute=minute
                    )
            # 스케줄 작업 추가
            today_date = datetime.datetime.now()
            if "%Y" in schedule.csv_path and "%m" in schedule.csv_path and "%d" in schedule.csv_path:
                formatted_csv_path = today_date.strftime(schedule.csv_path)
            else:
               # 포함되어 있지 않으면 원래 경로 사용
                formatted_csv_path = schedule.csv_path

            if "%Y" in schedule.group_csv_path and "%m" in schedule.group_csv_path and "%d" in schedule.group_csv_path:
                formatted_group_csv_path = today_date.strftime(schedule.group_csv_path)
            else:
               # 포함되어 있지 않으면 원래 경로 사용
                formatted_group_csv_path = schedule.group_csv_path


            print(formatted_csv_path,formatted_group_csv_path)
            scheduler.add_job(run_import_csv_thread, CronTrigger(hour=schedule.hour, minute=schedule.minute), args=[formatted_csv_path,formatted_group_csv_path])
            register_events(scheduler)
           # return JsonResponse({
           #     'status': 'success',
           #     'message': f'Scheduled CSV import for {day_of_week} at {hour}:{minute} with path: {csv_path}'
            #})

            return redirect('table_page')
        elif action == 'execute':
            if schedule:
                if not executing:
                    run_import_csv_thread(schedule.csv_path)
                    return JsonResponse({
                        'status': 'success',
                        'message': 'CSV import executed immediately.'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'CSV import is already running.'
                    })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No schedule found to execute.'
                })

def list_jobs(request):
    # 전체 작업 불러오기
    jobs = scheduler.get_jobs()
    if jobs:
        job_list = [f"Job ID: {job.id}, Next Run Time: {job.next_run_time}" for job in jobs]
        return HttpResponse("<br>".join(job_list))
    else:
        return HttpResponse("No jobs found")

