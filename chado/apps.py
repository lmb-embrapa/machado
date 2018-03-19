from django.apps import AppConfig
from chado import settings as dt_settings
from django.db.utils import ProgrammingError
import warnings


class ChadoConfig(AppConfig):
    name = 'chado'
    verbose_name = 'Django Chado'

    def ready(self):
        try:
            dt_settings.patch_all()
        except ProgrammingError as e:
            if str(e).startswith('relation "cvterm" does not exist'):
                warnings.warn("You need to run: 'python manage.py migrate'")
            pass
