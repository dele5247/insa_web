# Generated by Django 4.2.13 on 2024-06-09 01:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insa', '0003_department_dept_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='department',
            old_name='index',
            new_name='id',
        ),
    ]