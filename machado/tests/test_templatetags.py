# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests feature view."""

from django.test import TestCase, RequestFactory

from machado.templatetags import machado_extras


class MachadoExtrasTest(TestCase):
    """Tests Feature View."""

    def setUp(self):
        """Setup."""
        self.factory = RequestFactory()

    def test_param_replace(self):
        """Tests - param_replace."""
        request = self.factory.get("/find/?q=&page=1")
        context = {"request": request}
        result = machado_extras.param_replace(context, page=2)
        self.assertEqual("q=&page=2", result)

        request = self.factory.get("/find/?q=&selected_facets=so_term_exact:gene")
        context = {"request": request}
        result = machado_extras.param_replace(
            context, selected_facets="organism:Arabidopsis thaliana"
        )
        self.assertEqual(
            "q=&selected_facets=so_term_exact%3Agene&"
            "selected_facets=organism%3AArabidopsis+thaliana",
            result,
        )

    def test_remove_facet(self):
        """Tests - test_remove_facet."""
        request = self.factory.get(
            "/find/?q=&selected_facets=so_term_exact:gene&"
            "selected_facets=organism:Arabidopsis thaliana"
        )
        context = {"request": request}
        result = machado_extras.remove_facet(context, "organism")
        self.assertEqual("q=&selected_facets=so_term_exact%3Agene", result)
