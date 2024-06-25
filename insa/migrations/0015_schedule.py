# Generated by Django 4.2.13 on 2024-06-24 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insa', '0014_setting_group_csv_path_setting_user_csv_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv_path', models.CharField(max_length=255)),
                ('day_of_week', models.CharField(choices=[('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')], max_length=3)),
                ('hour', models.IntegerField()),
                ('minute', models.IntegerField()),
            ],
        ),
    ]
