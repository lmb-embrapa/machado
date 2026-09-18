"""Apps."""

# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

from django.apps import AppConfig


class MachadoConfig(AppConfig):
    """Machado config."""

    name = "machado"
    verbose_name = "machado"

    def ready(self):
        """Ready."""
        from django.core.checks import register

        from machado.caching import check_cache_directory

        register(check_cache_directory)
