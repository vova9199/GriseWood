from django.apps import AppConfig


class SawcrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SawCRM'

    def ready(self):
        import SawCRM.signals