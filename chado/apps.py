from django.apps import AppConfig
from chado import settings as dt_settings


class ChadoConfig(AppConfig):
    name = 'chado'
    verbose_name = 'Django Chado'

    def ready(self):
        dt_settings.patch_all()
