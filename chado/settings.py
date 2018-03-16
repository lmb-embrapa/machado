"""App settings file."""

from django.conf import settings
from importlib import import_module


def patch_root_urlconf():
    """Include the machado urls."""
    from django.conf.urls import include, url
    if hasattr(settings, 'ROOT_URLCONF'):
        urlconf_module = import_module(settings.ROOT_URLCONF)
        urlconf_module.urlpatterns = [
            url('chado/', include('chado.urls')),
        ] + urlconf_module.urlpatterns


def patch_all():
    """Apply patches."""
    patch_root_urlconf()
    settings.USE_THOUSAND_SEPARATOR = True
