# Generated by Django 4.2.13 on 2024-06-24 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insa', '0013_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='group_csv_path',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='setting',
            name='user_csv_path',
            field=models.CharField(max_length=255, null=True),
        ),
    ]