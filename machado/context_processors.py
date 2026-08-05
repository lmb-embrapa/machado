# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Template context processors for site-wide customization."""

import json
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# ── Default values for landing-page content ──────────────────────────────────
# These match the original hardcoded text so the app works unchanged
# when no MACHADO_SITE_* settings are defined.

DEFAULTS = {
    # Site-wide
    "MACHADO_ACCENT_COLOR": "steel",
    "MACHADO_SITE_TITLE": "Machado Genomics",
    "MACHADO_SITE_DESCRIPTION": ("Machado Genomics \u2014 biological data management"),
    # Hero section
    "MACHADO_HERO_TITLE": "Genomics Data Management Portal",
    "MACHADO_HERO_SUBTITLE": (
        "Explore, search, and visualize genomics sequences, annotations, "
        "and publications stored in the Chado database."
    ),
    # Feature card 1
    "MACHADO_FEATURE1_TITLE": "Multi-Format Data Loaders",
    "MACHADO_FEATURE1_TEXT": (
        "Ingest data seamlessly from standard bioinformatics formats "
        "including FASTA, GFF3, OBO, BibTeX, BLAST, InterProScan, and "
        "OrthoMCL directly into the Chado relational schema."
    ),
    "MACHADO_FEATURE1_ICON": "fas fa-file-import",
    # Feature card 2
    "MACHADO_FEATURE2_TITLE": "PostgreSQL Faceted Search",
    "MACHADO_FEATURE2_TEXT": (
        "Execute complex queries powered by PostgreSQL full-text search. "
        "Filter features by organism, sequence ontology terms, orthology, "
        "coexpression groups, and related publications."
    ),
    "MACHADO_FEATURE2_ICON": "fas fa-search",
    # Feature card 3
    "MACHADO_FEATURE3_TITLE": "Genome Browser Integration",
    "MACHADO_FEATURE3_TEXT": (
        "Interactive visual analysis of features. Machado Genomics API "
        "delivers data directly to the embedded JBrowse genome browser "
        "for sequence and annotation alignments."
    ),
    "MACHADO_FEATURE3_ICON": "fas fa-align-left",
    # How-it-works step 1
    "MACHADO_STEP1_TITLE": "Load Data",
    "MACHADO_STEP1_TEXT": (
        "Administrators run commands or use data tools to load genomic "
        "files into the database."
    ),
    # How-it-works step 2
    "MACHADO_STEP2_TITLE": "Index & Query",
    "MACHADO_STEP2_TEXT": (
        "PostgreSQL full-text index updates automatically, enabling fast, "
        "multi-faceted searches across millions of features."
    ),
    # How-it-works step 3
    "MACHADO_STEP3_TITLE": "Discover",
    "MACHADO_STEP3_TEXT": (
        "Users inspect features, view analysis results, download bulk "
        "data, and browse via JBrowse."
    ),
}


# ── Release notes (loaded once at module import time) ────────────────────────


def _load_release_notes():
    """Load release_notes.json from BASE_DIR, if it exists.

    Returns a list of dicts with keys: version, date, description.
    Returns an empty list if the file is missing or malformed.
    """
    base_dir = getattr(settings, "BASE_DIR", None)
    if base_dir is None:
        return []

    release_file = Path(base_dir) / "release_notes.json"
    if not release_file.is_file():
        return []

    try:
        with open(release_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            logger.warning(
                "release_notes.json: expected a JSON array, got %s",
                type(data).__name__,
            )
            return []
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load release_notes.json: %s", exc)
        return []


# Cache at module level — read once per server process.
_release_notes_cache = None


def _get_release_notes():
    """Return cached release notes, loading on first access."""
    global _release_notes_cache
    if _release_notes_cache is None:
        _release_notes_cache = _load_release_notes()
    return _release_notes_cache


# ── Context processor ────────────────────────────────────────────────────────


def machado_site(request):
    """Inject MACHADO_SITE_* values into every template context."""
    context = {}
    for setting_name, default_value in DEFAULTS.items():
        # Convert MACHADO_SITE_TITLE → machado_site_title
        context_key = setting_name.lower()
        context[context_key] = getattr(settings, setting_name, default_value)

    # Release notes
    context["machado_release_notes"] = _get_release_notes()

    # Mount-path prefix, used to namespace client-side storage keys when
    # multiple instances share a domain.
    context["machado_url_prefix"] = getattr(settings, "URL_PREFIX", "")

    return context
