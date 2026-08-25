# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Collapse FeatureSearchIndex.orthologs_coexpression to a boolean.

The column stored one JSON boolean per (orthologous-group member,
translation_of subject) pair -- averaging 162 elements per row and peaking
at 9627, about 1.2 billion elements and 747MB table-wide -- to encode what
the facet only ever asked as a single bit: does this feature's orthologous
group contain a coexpressed member? See
searchindex._compute_ortholog_flags for the full account.

The array form did not merely cost more, it did not work. Its facet count
counted pairs rather than rows, so it advertised 1,153,066,191 hits on a
7,564,658-row table, and the ``__contains`` filter paired with it searched
for the *string* "true" inside an array of JSON *booleans*, matching
nothing: selecting the facet always returned zero results.

The new value is recoverable from the old column, so this migrates the data
in place with one UPDATE rather than requiring a full rebuild_search_index
run (days on a production corpus). ``@> 'true'::jsonb`` asks whether the
array contains a true element, which is exactly ``any(flags)``.

Not reversible: collapsing the per-pair flags to one bit discards the
per-member detail, and nothing reads it back.

Deliberately transactional, unlike 0009's AddIndexConcurrently on this same
table. 0009 only added indexes, so a half-applied run lost nothing and
avoiding its write lock was the only concern worth optimising for. Here the
run drops the column the new value is derived from: a partial application
would leave the boolean unpopulated with no source left to recompute it
from, short of a multi-day rebuild_search_index. All-or-nothing is worth
more than a briefly held lock, so this keeps the default atomic behaviour
and a plain AddIndex.
"""

from django.db import migrations, models


def forwards(apps, schema_editor):
    """Set the boolean from the old array, then drop the array column."""
    schema_editor.execute("""
        UPDATE machado_featuresearchindex
        SET orthologs_coexpression_bool = (orthologs_coexpression @> 'true'::jsonb)
        """)


class Migration(migrations.Migration):
    """Replace the JSON array column with an indexed boolean."""

    dependencies = [
        ("machado", "0010_clean_bibtex_pub_titles"),
    ]

    operations = [
        # Add the replacement alongside the original so the old values are
        # still readable when forwards() derives the new ones from them.
        migrations.AddField(
            model_name="featuresearchindex",
            name="orthologs_coexpression_bool",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="featuresearchindex",
            name="orthologs_coexpression",
        ),
        migrations.RenameField(
            model_name="featuresearchindex",
            old_name="orthologs_coexpression_bool",
            new_name="orthologs_coexpression",
        ),
        migrations.AddIndex(
            model_name="featuresearchindex",
            index=models.Index(
                fields=["orthologs_coexpression"], name="fsi_orth_coexp_idx"
            ),
        ),
    ]
