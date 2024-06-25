from django import forms
from .models import Employee, Department, Setting

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            field.name: forms.TextInput(attrs={'class': 'form-control'}) for field in Employee._meta.fields
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        widgets = {
            field.name: forms.TextInput(attrs={'class': 'form-control'}) for field in Department._meta.fields
        }

class SettingForm(forms.ModelForm):
    class Meta:
        model = Setting
        fields = '__all__'
        widgets = {
            field.name: forms.TextInput(attrs={'class': 'form-control'}) for field in Setting._meta.fields
        }
    def __init__(self, *args, **kwargs):
        super(SettingForm, self).__init__(*args, **kwargs)
        self.fields['site_name'].widget.attrs['disabled'] = True

