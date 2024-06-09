from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Department, Setting
from .forms import EmployeeForm, DepartmentForm, SettingForm
from django.contrib.auth.decorators import login_required


sets=Setting.objects.all()

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def input_page(request):
    return render(request, 'input_page.html')


@login_required
def table_page(request):
    data = Employee.objects.all()
    return render(request, 'table_page.html', {'data': data, 'sets': sets})

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

    return render(request, 'employee_form.html', {'form': form, 'sets': sets})

@login_required
def department_table_page(request):
    data = Department.objects.all()
    return render(request, 'department_table_page.html', {'data': data, 'sets': sets})

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

    return render(request, 'department_form.html', {'form': form, 'sets': sets})

def settings(request):
    setting = Setting.objects.first()
    if not setting:
        setting = Setting.objects.create(site_name='Default Site', admin_email='admin@example.com')
    if request.method == 'POST':
        print("a")
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('settings')
    else:
        form = SettingForm(instance=setting)
    return render(request, 'settings.html', {'form': form, 'sets': sets})
