# Generated by Django 4.2.2 on 2024-01-03 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SawCRM', '0004_alter_completedact_delivery_point_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='completedact',
            options={'ordering': ['-transport_date', 'loading_point', 'delivery_point', '-created_at'], 'verbose_name': 'Completed Act', 'verbose_name_plural': 'Completed Acts'},
        ),
    ]
