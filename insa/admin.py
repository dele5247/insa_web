from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'employee_number', 'employee_name', 'chinese_name', 'english_name', 
        'employment_status', 'personal_id', 'hr_department', 
        'salary_department', 'work_department', 'expense_department', 
        'workshop_code', 'position', 'birthdate', 'ssn'
    )
