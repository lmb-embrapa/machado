# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""System checks for a project's machado configuration.

machado used to apply these settings itself, by mutating django.conf.settings
from AppConfig.ready(). It no longer does: the shipped project template states
them explicitly instead. These checks are what makes the removal safe -- a
project that upgraded without updating its settings.py and urls.py fails
``manage.py check`` with an actionable message rather than 404ing or redirecting
into nowhere at runtime.

Every check reads settings only. None touches the database, so they are safe to
run during ``migrate`` on a fresh, empty project.
"""

from django.conf import settings
from django.core.checks import Error
from django.urls import NoReverseMatch, reverse

UPGRADE_DOC = (
    "See the 'Upgrading from a version before the settings change' section of "
    "docs/01-installation.md."
)

REQUIRED_MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

CONTEXT_PROCESSOR = "machado.context_processors.machado_site"


def check_machado_settings(app_configs, **kwargs):
    """Report every piece of machado configuration the project is missing."""
    errors = []

    try:
        reverse("home")
    except NoReverseMatch:
        errors.append(
            Error(
                "machado's URLs are not reachable from ROOT_URLCONF.",
                hint=(
                    'Add path("", include("machado.urls")) to your project\'s '
                    "urlpatterns. " + UPGRADE_DOC
                ),
                id="machado.E001",
            )
        )

    processors = set()
    for template in getattr(settings, "TEMPLATES", []):
        processors.update(template.get("OPTIONS", {}).get("context_processors", []))
    if CONTEXT_PROCESSOR not in processors:
        errors.append(
            Error(
                "The machado_site context processor is not registered.",
                hint=(
                    'Add "{}" to OPTIONS["context_processors"] of your '
                    "TEMPLATES entry. {}".format(CONTEXT_PROCESSOR, UPGRADE_DOC)
                ),
                id="machado.E002",
            )
        )

    if not getattr(settings, "MACHADO_VALID_TYPES", None):
        errors.append(
            Error(
                "MACHADO_VALID_TYPES is not set.",
                hint=(
                    "Set it to the feature types this instance serves, e.g. "
                    '["gene", "mRNA", "polypeptide"]. ' + UPGRADE_DOC
                ),
                id="machado.E003",
            )
        )

    middleware = set(getattr(settings, "MIDDLEWARE", []))
    missing = [m for m in REQUIRED_MIDDLEWARE if m not in middleware]
    if missing:
        errors.append(
            Error(
                "Required middleware is missing: {}.".format(", ".join(missing)),
                hint="Add them to MIDDLEWARE. " + UPGRADE_DOC,
                id="machado.E004",
            )
        )

    if not getattr(settings, "LOGIN_URL", None):
        errors.append(
            Error(
                "LOGIN_URL is not set.",
                hint=(
                    'Set LOGIN_URL = "login". It is the route NAME, not a path: '
                    "machado mounts django.contrib.auth.urls under "
                    "loader/accounts/, so the stock /accounts/login/ would 404. "
                    + UPGRADE_DOC
                ),
                id="machado.E005",
            )
        )

    return errors
