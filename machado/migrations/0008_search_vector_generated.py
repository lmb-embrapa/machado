# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Convert FeatureSearchIndex.search_vector into a generated column.

Hand-written rather than generated: `makemigrations` for this app also
proposes ~207 state-only CreateModel operations for the unmanaged Chado
tables that migration 0001 loads from a third-party SQL dump. Those are
noise, so only the one real schema change is expressed here.

PostgreSQL cannot attach a generation expression to an existing column, so
the column is dropped and re-added. The dependent GIN index is recreated
afterwards -- without it every search degrades to a sequential scan.
"""

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):
    """Make search_vector a STORED generated column."""

    dependencies = [
        ("machado", "0007_update_history_tracking"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "DROP INDEX IF EXISTS fsi_search_gin;",
                        "ALTER TABLE machado_featuresearchindex "
                        "DROP COLUMN IF EXISTS search_vector;",
                        "ALTER TABLE machado_featuresearchindex "
                        "ADD COLUMN search_vector tsvector "
                        "GENERATED ALWAYS AS "
                        "(to_tsvector('english'::regconfig, autocomplete_text)) "
                        "STORED;",
                        "CREATE INDEX fsi_search_gin ON "
                        "machado_featuresearchindex USING gin (search_vector);",
                    ],
                    reverse_sql=[
                        "DROP INDEX IF EXISTS fsi_search_gin;",
                        "ALTER TABLE machado_featuresearchindex "
                        "DROP COLUMN IF EXISTS search_vector;",
                        "ALTER TABLE machado_featuresearchindex "
                        "ADD COLUMN search_vector tsvector;",
                        "CREATE INDEX fsi_search_gin ON "
                        "machado_featuresearchindex USING gin (search_vector);",
                    ],
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="featuresearchindex",
                    name="search_vector",
                    field=models.GeneratedField(
                        expression=django.contrib.postgres.search.SearchVector(
                            "autocomplete_text", config="english"
                        ),
                        output_field=(
                            django.contrib.postgres.search.SearchVectorField(null=True)
                        ),
                        db_persist=True,
                    ),
                ),
            ],
        ),
    ]
