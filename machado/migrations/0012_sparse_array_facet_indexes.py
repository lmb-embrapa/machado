# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Partial indexes over the non-empty rows of the sparse array facets.

Counting a JSON-array facet means unnesting its array, which lives in the
heap and no full index can cover, so the aggregate scanned all 7,564,658
rows to reach the ~2% that hold a value. On the production corpus
biomaterial and treatment each carry a value on 159,926 rows (2.11%) and
doi on none at all -- and doi still spent ~1.2s per page load proving it.

These index only the rows a facet can actually contribute from: 3.5MB for
biomaterial and treatment, 8KB for doi, against ~50MB for a full index on
the same table. Measured with them in place: biomaterial 1.17s -> 0.13s,
doi 1.31s -> 0.001s, in both the unfiltered and filtered query shapes.

Only usable while FeatureSearchView._compute_array_facet emits the matching
``<> '[]'`` predicate; the two have to stay in the same shape. Postgres
matches ``field <> '[]'::jsonb`` against the ``NOT (field = '[]'::jsonb)``
condition Django generates here, via the operator's negator -- verified in
the plan (Bitmap Index Scan) rather than assumed.

Not applied to "analyses": every row carries a value there, so the partial
index would cover the whole table and buy nothing (measured neutral, 1.57s
vs 1.61s).

Uses CONCURRENTLY, following 0009: this only adds indexes, so a partial
application loses nothing and not holding a write lock on a multi-million
row table is the concern worth optimising for. (0011 deliberately went the
other way, because it dropped the column its new value was derived from.)
"""

from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add partial indexes for the sparse JSON-array facet columns."""

    atomic = False

    dependencies = [
        ("machado", "0011_orthologs_coexpression_boolean"),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="featuresearchindex",
            index=models.Index(
                fields=["feature"],
                name="fsi_biomaterial_ne_idx",
                condition=~models.Q(biomaterial=[]),
            ),
        ),
        AddIndexConcurrently(
            model_name="featuresearchindex",
            index=models.Index(
                fields=["feature"],
                name="fsi_treatment_ne_idx",
                condition=~models.Q(treatment=[]),
            ),
        ),
        AddIndexConcurrently(
            model_name="featuresearchindex",
            index=models.Index(
                fields=["feature"],
                name="fsi_doi_ne_idx",
                condition=~models.Q(doi=[]),
            ),
        ),
    ]
