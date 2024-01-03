# Generated by Django 4.2.2 on 2023-12-25 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_customuser_groups_customuser_user_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='created_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата сворення'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('EMPLOYEE', 'Працівник'), ('DRIVER', 'Водій'), ('TRACK DRIVER', 'Далекобійник'), ('ENGINEER', 'Інженер'), ('MANAGER', 'Менеджер'), ('COUNTER', 'Бухгалтер'), ('DIRECTOR', 'Директор')], default='EMPLOYEE', max_length=15, verbose_name='Роль'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата оновлення'),
        ),
    ]