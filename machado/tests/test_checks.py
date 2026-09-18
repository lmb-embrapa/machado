# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for the machado settings system checks."""

from django.conf import settings
from django.test import TestCase, override_settings

from machado.checks import check_machado_settings

#: This module doubles as a URLconf for the E001 test: a valid one that
#: contains none of machado's routes. A module with no ``urlpatterns`` would
#: raise AttributeError instead of the NoReverseMatch the check catches.
urlpatterns = []

FULL_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

FULL_TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["machado.context_processors.machado_site"]},
    }
]


def _ids(errors):
    """Return the check ids of a list of check messages."""
    return {error.id for error in errors}


class MachadoSettingsCheckTest(TestCase):
    """Each missing piece of configuration reports its own error."""

    def test_a_correctly_configured_project_reports_nothing(self):
        """The test project itself must pass its own check."""
        self.assertEqual(check_machado_settings(None), [])

    @override_settings(ROOT_URLCONF="machado.tests.test_checks")
    def test_missing_machado_urls_reports_e001(self):
        """A URLconf without machado's routes is an error."""
        self.assertIn("machado.E001", _ids(check_machado_settings(None)))

    @override_settings(TEMPLATES=[])
    def test_missing_context_processor_reports_e002(self):
        """The machado_site context processor is required."""
        self.assertIn("machado.E002", _ids(check_machado_settings(None)))

    def test_missing_valid_types_reports_e003(self):
        """MACHADO_VALID_TYPES has no usable default.

        override_settings cannot remove a setting, only replace one. Entering
        it with no arguments swaps in a UserSettingsHolder that supports
        deletion and is discarded on exit, which is how the setting is made
        genuinely absent rather than merely empty.
        """
        with override_settings():
            del settings.MACHADO_VALID_TYPES
            self.assertIn("machado.E003", _ids(check_machado_settings(None)))

    @override_settings(MIDDLEWARE=[])
    def test_missing_middleware_reports_e004(self):
        """Session, auth and messages middleware are all required."""
        self.assertIn("machado.E004", _ids(check_machado_settings(None)))

    @override_settings(LOGIN_URL=None)
    def test_missing_login_url_reports_e005(self):
        """LOGIN_URL must name the login route."""
        self.assertIn("machado.E005", _ids(check_machado_settings(None)))

    @override_settings(LOGIN_URL="/accounts/login/")
    def test_login_url_still_at_django_default_reports_e005(self):
        """Django's truthy default is also wrong: it is a path, not a name."""
        self.assertIn("machado.E005", _ids(check_machado_settings(None)))

    @override_settings(USE_TZ=True)
    def test_use_tz_true_reports_e006(self):
        """The chado schema stores naive timestamps."""
        self.assertIn("machado.E006", _ids(check_machado_settings(None)))

    @override_settings(USE_TZ=False)
    def test_use_tz_false_does_not_report_e006(self):
        """USE_TZ = False is exactly what machado expects."""
        self.assertNotIn("machado.E006", _ids(check_machado_settings(None)))

    @override_settings(LOGIN_REDIRECT_URL="/accounts/profile/")
    def test_login_redirect_url_still_at_django_default_reports_e007(self):
        """Django's default 404s in machado."""
        self.assertIn("machado.E007", _ids(check_machado_settings(None)))

    @override_settings(LOGOUT_REDIRECT_URL=None)
    def test_missing_logout_redirect_url_reports_e008(self):
        """LOGOUT_REDIRECT_URL has no usable default."""
        self.assertIn("machado.E008", _ids(check_machado_settings(None)))

    @override_settings(MIDDLEWARE=FULL_MIDDLEWARE, TEMPLATES=FULL_TEMPLATES)
    def test_a_complete_configuration_reports_no_middleware_or_template_error(self):
        """A project with all the pieces reports neither E002 nor E004."""
        ids = _ids(check_machado_settings(None))
        self.assertNotIn("machado.E002", ids)
        self.assertNotIn("machado.E004", ids)
