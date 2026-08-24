# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Backfill Pub.title for records imported before clean_bibtex_title existed.

The BibTeX loader used to only strip a single leading/trailing brace from a
title, so titles that carried BibTeX case-protection braces or LaTeX
formatting/symbol commands anywhere else -- "{GWAS}", "\\textit{{FABP1}}",
"Gs$\\upalpha$" -- kept that raw markup in the database. New imports are
already clean (see loaders/publication.py); this is a one-time fix for the
titles already stored.

This imports the loader's cleaning function rather than duplicating its
logic: unlike a schema operation, clean_bibtex_title has no dependency on
model state, so there's nothing here that a historical model snapshot would
need to protect against future changes to it -- and duplicating ~50 lines
of regex would just be a second copy to keep in sync when the loader's own
test suite (test_loaders_publication.py) is what actually exercises it.

Uses the real Pub model rather than apps.get_model: Pub is unmanaged and,
like ~207 other Chado tables, was never given a CreateModel migration (see
0008's docstring for the same situation), so it has no historical state for
apps.get_model to return.

Not reversible: the raw BibTeX markup this removes is not recoverable from
the cleaned text.
"""

from django.db import migrations

from machado.loaders.publication import clean_bibtex_title
from machado.models import Pub


def forwards(apps, schema_editor):
    """Re-clean every stored title, updating only the ones that change."""
    to_update = []
    for pub in Pub.objects.exclude(title__isnull=True).only("pub_id", "title"):
        cleaned = clean_bibtex_title(pub.title)
        if cleaned != pub.title:
            pub.title = cleaned
            to_update.append(pub)

    if to_update:
        Pub.objects.bulk_update(to_update, ["title"], batch_size=500)


class Migration(migrations.Migration):
    """Clean up leftover BibTeX/LaTeX markup in already-imported Pub titles."""

    dependencies = [
        ("machado", "0009_add_orthology_coexpression_index"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
