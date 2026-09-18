# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for the shared display/DOI rules."""

from django.test import TestCase

from machado import display


class DisplayContractTest(TestCase):
    """The constants carry an invariant the two call sites depend on."""

    def test_prop_types_is_a_superset_of_display_fallback(self):
        """A fallback name missing from PROP_TYPES silently loses a step."""
        self.assertTrue(set(display.DISPLAY_FALLBACK) <= set(display.PROP_TYPES))


class ResolveDisplayTest(TestCase):
    """The display fallback chain."""

    def test_prefers_the_display_prop(self):
        """display wins over every later name."""
        props = {"display": ["chosen"], "product": ["ignored"]}
        self.assertEqual(display.resolve_display(props), "chosen")

    def test_falls_back_through_the_chain(self):
        """An absent name moves on to the next."""
        props = {"note": ["last resort"]}
        self.assertEqual(display.resolve_display(props), "last resort")

    def test_returns_none_when_nothing_is_set(self):
        """No props at all resolves to None."""
        self.assertIsNone(display.resolve_display({}))

    def test_takes_the_first_value_by_rank(self):
        """Duplicated props resolve to the lowest rank, never an exception."""
        self.assertEqual(display.resolve_display({"product": ["a", "b"]}), "a")

    def test_a_null_valued_prop_stops_the_chain(self):
        """A present-but-NULL prop yields [None], a truthy list, so it wins."""
        props = {"product": [None], "description": ["not reached"]}
        self.assertIsNone(display.resolve_display(props))


class FormatAnnotationTest(TestCase):
    """The annotation label rule."""

    def test_without_dois_is_the_bare_value(self):
        """No DOIs means no parenthetical."""
        self.assertEqual(display.format_annotation("kinase", []), "kinase")

    def test_appends_a_single_doi(self):
        """One DOI renders in a DOI: parenthetical."""
        self.assertEqual(
            display.format_annotation("kinase", ["10.1/a"]),
            "kinase (DOI:10.1/a)",
        )

    def test_joins_several_dois_with_commas(self):
        """Several DOIs share one parenthetical, comma-separated."""
        self.assertEqual(
            display.format_annotation("kinase", ["10.1/a", "10.2/b"]),
            "kinase (DOI:10.1/a, 10.2/b)",
        )


class GroupPropsTest(TestCase):
    """Row grouping is pure and preserves the query's order."""

    def test_groups_by_feature_then_type_preserving_order(self):
        """Values arrive in the order the rows did."""
        rows = [
            {
                "featureprop_id": 1,
                "feature_id": 7,
                "type__name": "product",
                "value": "first",
            },
            {
                "featureprop_id": 2,
                "feature_id": 7,
                "type__name": "product",
                "value": "second",
            },
            {
                "featureprop_id": 3,
                "feature_id": 8,
                "type__name": "note",
                "value": "other",
            },
        ]
        self.assertEqual(
            display.group_props(rows),
            {7: {"product": ["first", "second"]}, 8: {"note": ["other"]}},
        )

    def test_no_rows_is_an_empty_map(self):
        """An empty row list groups to an empty dict."""
        self.assertEqual(display.group_props([]), {})
