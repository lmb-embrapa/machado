# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""App settings file."""

from django.conf import settings
from importlib import import_module


def patch_installed_apps():
    """Include dependencies to INSTALLED_APPS."""
    settings.INSTALLED_APPS.append('corsheaders')


def patch_middleware():
    """Include dependencies to MIDDLEWARE."""
    settings.MIDDLEWARE.append(
        'corsheaders.middleware.CorsMiddleware')
    settings.MIDDLEWARE.append(
        'django.contrib.sessions.middleware.SessionMiddleware')
    settings.MIDDLEWARE.append(
        'django.contrib.auth.middleware.AuthenticationMiddleware')
    settings.MIDDLEWARE.append(
        'django.contrib.messages.middleware.MessageMiddleware')


def patch_root_urlconf():
    """Include the machado urls."""
    from django.conf.urls import include, url
    if hasattr(settings, 'ROOT_URLCONF'):
        urlconf_module = import_module(settings.ROOT_URLCONF)
        urlconf_module.urlpatterns = [
            url('machado/', include('machado.urls')),
        ] + urlconf_module.urlpatterns


def patch_templates():
    """Include dependencies to TEMPLATE."""
    if len(settings.TEMPLATES) > 0:
        for template in settings.TEMPLATES:
            if template['BACKEND'] == 'django.template.backends.django.'\
               'DjangoTemplates':
                template['OPTIONS']['context_processors'].append(
                    'machado.context_processors.organism_processor')
    else:
        settings.TEMPLATES.append(
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                        'machado.context_processors.organism_processor'
                    ]
                }
            }
        )


def patch_all():
    """Apply patches."""
    patch_root_urlconf()
    patch_installed_apps()
    patch_middleware()
    patch_templates()

    settings.USE_THOUSAND_SEPARATOR = True
    settings.APPEND_SLASH = True
    settings.CORS_ORIGIN_ALLOW_ALL = True
    settings.USE_TZ = False
