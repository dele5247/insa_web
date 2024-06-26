# Generated by Django 4.2.13 on 2024-06-09 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_number', models.CharField(max_length=20)),
                ('employee_name', models.CharField(max_length=100)),
                ('chinese_name', models.CharField(max_length=100)),
                ('english_name', models.CharField(max_length=100)),
                ('employment_status', models.CharField(max_length=10)),
                ('personal_id', models.CharField(max_length=20)),
                ('hr_department', models.CharField(max_length=10)),
                ('salary_department', models.CharField(max_length=10)),
                ('work_department', models.CharField(max_length=10)),
                ('expense_department', models.CharField(max_length=10)),
                ('workshop_code', models.CharField(max_length=10)),
                ('position', models.CharField(max_length=10)),
                ('birthdate', models.CharField(max_length=10)),
                ('ssn', models.CharField(max_length=20)),
            ],
        ),
    ]
