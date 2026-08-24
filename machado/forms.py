# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Search forms — PostgreSQL full-text search."""

from django import forms
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q, Value
from django.db import models

from machado.models import FeatureSearchIndex

# Facets that are stored as JSON arrays (need __contains lookups)
_ARRAY_FACETS = {
    "analyses",
    "biomaterial",
    "treatment",
    "doi",
    "orthologs_coexpression",
}

# The "analyses" facet uses AND logic; all others use OR.
_AND_FACETS = {"analyses"}

# Django's BooleanField.to_python only accepts "True"/"1"/"False"/"0" (case
# sensitive), but facet values arrive as raw query-string text such as
# "true"/"FALSE". Normalize any case of true/false to Python bool so
# scalar BooleanField facets don't raise a ValidationError.
def _normalize_facet_value(value):
    """Convert a boolean-like facet string to a Python bool, else pass through."""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


class FeatureSearchForm(forms.Form):
    """Search form backed by PostgreSQL full-text search."""

    q = forms.CharField(required=False)

    def search(self, selected_facets=None):
        """Return a filtered queryset of FeatureSearchIndex rows."""
        qs = FeatureSearchIndex.objects.all()
        q = self.cleaned_data.get("q", "").strip()

        # ── Apply facet filters ──────────────────────────────────────────
        if selected_facets:
            qs = self._apply_facets(qs, selected_facets)

        # ── Apply full-text query ────────────────────────────────────────
        if q:
            # Save the faceted queryset to use in fallback if FTS fails
            base_qs = qs

            if "*" in q:
                # Handle wildcard search: "abc*" -> "abc:*"
                terms = [f"{t[:-1]}:*" if t.endswith("*") else t for t in q.split()]
                query = SearchQuery(
                    " & ".join(terms), config="english", search_type="raw"
                )
            else:
                # Standard websearch (supports quotes, +, -)
                query = SearchQuery(q, config="english", search_type="websearch")

            qs = base_qs.filter(search_vector=query).annotate(
                rank=SearchRank("search_vector", query)
            )

            # Substring fallback: if no FTS results, try partial matching on key fields
            if not qs.exists():
                clean_q = q.replace("*", "")
                qs = base_qs.filter(
                    Q(uniquename__icontains=clean_q)
                    | Q(name__icontains=clean_q)
                    | Q(display__icontains=clean_q)
                ).annotate(rank=Value(0.0, output_field=models.FloatField()))

        return qs

    @staticmethod
    def _apply_facets(qs, selected_facets):
        """Apply facet filters with AND for 'analyses', OR for others."""
        grouped = {}
        for facet_str in selected_facets:
            field, value = facet_str.split(":", 1)
            grouped.setdefault(field, []).append(value)

        for field, values in grouped.items():
            if field in _AND_FACETS:
                # AND logic: every selected value must be present
                for v in values:
                    qs = qs.filter(**{f"{field}__contains": [v]})
            elif field in _ARRAY_FACETS:
                # OR logic for array fields
                q_obj = Q()
                for v in values:
                    q_obj |= Q(**{f"{field}__contains": [v]})
                qs = qs.filter(q_obj)
            else:
                # Scalar fields — OR via __in
                values = [_normalize_facet_value(v) for v in values]
                qs = qs.filter(**{f"{field}__in": values})

        return qs
