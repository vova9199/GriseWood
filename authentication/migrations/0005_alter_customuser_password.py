# Generated by Django 4.2.2 on 2023-12-01 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Пароль'),
        ),
    ]
