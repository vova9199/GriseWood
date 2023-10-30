from django.db.models.signals import post_migrate
from django.dispatch import receiver

from . import apps
from .models import WoodType


@receiver(post_migrate)
def add_initial_data(sender, **kwargs):
    if sender.name == 'SawCRM' and kwargs.get('verbosity') == 0:

        # WoodType initial data
        woodtype_name = ['ялиця', 'дуб', 'ялина']
            # Додати ваші початкові записи до таблиці WoodType
        for name in woodtype_name:
            WoodType.objects.get_or_create(name=name)
