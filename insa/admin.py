from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'employee_id', 'sAMAccountName', 'upn', 'display_name',
        'last_name', 'first_name', 'description', 'title', 'department',
        'company', 'email', 'employment_status', 'group'
    )
