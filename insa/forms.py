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
        if 'ad_password' in self.fields:
            self.fields['ad_password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
            self.fields['ad_password'].required = False
        if 'ftp_password' in self.fields:
            self.fields['ftp_password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
            self.fields['ftp_password'].required = False

    def clean_ad_password(self):
        # 비밀번호 필드가 비어 있는 경우 기존 비밀번호를 유지
        ad_password = self.cleaned_data.get('ad_password')
        if not ad_password and self.instance.pk:
            return self.instance.ad_password
        return ad_password
    def clean_ftp_password(self):
        # 비밀번호 필드가 비어 있는 경우 기존 비밀번호를 유지
        ftp_password = self.cleaned_data.get('ftp_password')
        if not ftp_password and self.instance.pk:
            return self.instance.ftp_password
        return ftp_password

