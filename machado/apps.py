"""Apps."""

# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

import warnings

from django.apps import AppConfig
from django.db.utils import ProgrammingError

from machado import settings as dt_settings


class MachadoConfig(AppConfig):
    """Machado config."""

    name = "machado"
    verbose_name = "machado"

    def ready(self):
        """Ready."""
        from django.core.checks import register

        from machado.caching import check_cache_directory

        register(check_cache_directory)

        try:
            dt_settings.patch_all()
            from machado.models import Organism
            from machado.decorators import machado_organism_methods

            machado_organism_methods()(Organism)
        except ProgrammingError as e:
            if str(e).startswith('relation "cvterm" does not exist'):
                warnings.warn("You need to run: 'python manage.py migrate'")
            pass
