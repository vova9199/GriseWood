# Generated by Django 4.2.2 on 2023-12-01 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('EMPLOYEE', 'Працівник'), ('ENGINEER', 'Інженер'), ('MANAGER', 'Менеджер'), ('COUNTER', 'Бухгалтер'), ('DIRECTOR', 'Директор')], default='EMPLOYEE', max_length=15),
        ),
    ]
