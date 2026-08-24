# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Index FeatureSearchIndex.orthology and .coexpression.

Hand-written rather than generated: `makemigrations` for this app also
proposes ~207 state-only CreateModel operations for the unmanaged Chado
tables that migration 0001 loads from a third-party SQL dump (see 0008 for
the same note). Those are noise, so only the two real indexes are
expressed here.

Uses CONCURRENTLY so building the index on the multi-million-row
machado_featuresearchindex table doesn't hold a lock that blocks writes.
CONCURRENTLY cannot run inside a transaction, hence atomic = False.
"""

from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add btree indexes on orthology and coexpression."""

    atomic = False

    dependencies = [
        ("machado", "0008_search_vector_generated"),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="featuresearchindex",
            index=models.Index(fields=["orthology"], name="fsi_orthology_idx"),
        ),
        AddIndexConcurrently(
            model_name="featuresearchindex",
            index=models.Index(fields=["coexpression"], name="fsi_coexpression_idx"),
        ),
    ]
