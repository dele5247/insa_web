from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings/', views.settings_view, name='settings_view'),
    path('table/', views.table_page, name='table_page'),
    path('employee_form/', views.employee_form, name='employee_form'),
    path('employee_form/<int:id>/', views.employee_form, name='employee_edit_form'),
    path('departments/', views.department_table_page, name='department_table_page'),
    path('department_form/', views.department_form, name='department_form'),
    path('department_form/<int:id>/', views.department_form, name='department_edit_form'),
    path('log/', views.log_table_page, name='log_table_page'),
    path('lockscreen/', views.lockscreen, name='lockscreen'),
    path('schedule-import-csv/', views.schedule_import_csv, name='schedule_import_csv'),
    path('list-jobs/', views.list_jobs, name='list_jobs'),
]

