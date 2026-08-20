# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Bootstrap a new machado project with pre-configured Django settings."""

import argparse
import shutil
import stat
import sys
from pathlib import Path

# ── .env template ────────────────────────────────────────────────────────────
_ENV_EXAMPLE = """\
# ── machado environment configuration ────────────────────────────────────────
# Copy this file to .env and edit the values below.

# ── Required ─────────────────────────────────────────────────────────────────
SECRET_KEY=change-me-to-a-random-string
DATABASE_URL=postgres://username:password@localhost:5432/yourdatabase

# ── Django ───────────────────────────────────────────────────────────────────
# DEBUG=True
# ALLOWED_HOSTS=localhost,127.0.0.1
# CSRF_TRUSTED_ORIGINS=https://example.com
# STATIC_URL=/static/
# STATIC_ROOT=staticfiles
# TIME_ZONE=UTC

# ── Multi-instance deployment (optional) ─────────────────────────────────────
# Set this instance's mount path when running more than one machado instance
# on the same domain (e.g. different Apache subpaths on the same machine), so
# session/CSRF cookies and browser storage don't collide between instances.
# URL_PREFIX=/demo

# ── JBrowse integration (optional) ───────────────────────────────────────────
# MACHADO_JBROWSE_URL=http://localhost/jbrowse
# MACHADO_JBROWSE_OFFSET=1200
# MACHADO_JBROWSE_TRACKS=

# ── Feature types for search indexing (optional) ─────────────────────────────
# MACHADO_VALID_TYPES=gene,mRNA,polypeptide

# ── Landing page customization (optional) ────────────────────────────────────
# All values below have sensible defaults; override only what you need.
# A feature-card, how-it-works-step, features-section, or Acknowledgements
# title/text set to an empty string hides that section. Acknowledgements is
# empty (hidden) by default; set MACHADO_ACKNOWLEDGEMENTS_TEXT to show it.
#
# MACHADO_ACCENT_COLOR values: steel, teal, sage, amber, graphite, ruby,
# indigo, emerald, coral, plum
# MACHADO_ACCENT_COLOR=steel
# MACHADO_SITE_TITLE=Machado Genomics
# MACHADO_SITE_DESCRIPTION=Machado Genomics — biological data management
# MACHADO_HERO_TITLE=Genomics Data Management Portal
# MACHADO_HERO_SUBTITLE=Explore, search, and visualize genomics sequences, annotations, and publications stored in the Chado database.
# MACHADO_FEATURES_TITLE=Key Features & Capabilities
# MACHADO_FEATURES_SUBTITLE=A comprehensive ecosystem designed for biological database curation and research.
# MACHADO_FEATURE1_TITLE=Multi-Format Data Loaders
# MACHADO_FEATURE1_TEXT=Ingest data seamlessly from standard bioinformatics formats including FASTA, GFF3, OBO, BibTeX, BLAST, InterProScan, and OrthoMCL directly into the Chado relational schema.
# MACHADO_FEATURE1_ICON=fas fa-file-import
# MACHADO_FEATURE2_TITLE=PostgreSQL Faceted Search
# MACHADO_FEATURE2_TEXT=Execute complex queries powered by PostgreSQL full-text search. Filter features by organism, sequence ontology terms, orthology, coexpression groups, and related publications.
# MACHADO_FEATURE2_ICON=fas fa-search
# MACHADO_FEATURE3_TITLE=Genome Browser Integration
# MACHADO_FEATURE3_TEXT=Interactive visual analysis of features. Machado Genomics API delivers data directly to the embedded JBrowse genome browser for sequence and annotation alignments.
# MACHADO_FEATURE3_ICON=fas fa-align-left
# MACHADO_STEP1_TITLE=Load Data
# MACHADO_STEP1_TEXT=Administrators run commands or use data tools to load genomic files into the database.
# MACHADO_STEP2_TITLE=Index & Query
# MACHADO_STEP2_TEXT=PostgreSQL full-text index updates automatically, enabling fast, multi-faceted searches across millions of features.
# MACHADO_STEP3_TITLE=Discover
# MACHADO_STEP3_TEXT=Users inspect features, view analysis results, download bulk data, and browse via JBrowse.
# MACHADO_ACKNOWLEDGEMENTS_TITLE=Acknowledgements
# MACHADO_ACKNOWLEDGEMENTS_TEXT=
# MACHADO_FOOTER_COPYRIGHT=© 2026 Embrapa. All rights reserved.
# MACHADO_FOOTER_TEXT=

# EMAIL_URL=smtp://user:password@smtp.example.com:587/?tls=True
"""


def _get_random_secret_key():
    """Generate a random SECRET_KEY suitable for Django."""
    from django.core.management.utils import get_random_secret_key

    return get_random_secret_key()


def main():
    """Entry point for the ``machado-startproject`` console script."""
    parser = argparse.ArgumentParser(
        prog="machado-startproject",
        description="Create a new machado project with pre-configured Django settings.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory for the new project (default: current directory).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in the target directory.",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=1,
        help="Verbosity level: 0=silent, 1=normal, 2=verbose (default: 1).",
    )
    args = parser.parse_args()
    verbose = args.verbosity >= 1

    target = Path(args.directory).resolve()
    template = Path(__file__).resolve().parent.parent / "project_template"

    if not template.is_dir():
        if verbose:
            print(
                f"Error: project template not found at {template}",
                file=sys.stderr,
            )
        sys.exit(1)

    # ── Copy template files ──────────────────────────────────────────────────
    target.mkdir(parents=True, exist_ok=True)

    for src_path in sorted(template.rglob("*")):
        if src_path.is_dir():
            continue
        # Skip __pycache__ and .pyc files
        if "__pycache__" in src_path.parts or src_path.suffix == ".pyc":
            continue

        rel = src_path.relative_to(template)
        dest = target / rel

        if dest.exists() and not args.overwrite:
            if verbose:
                print(f"  skip (exists): {rel}")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest)
        if verbose:
            print(f"  created: {rel}")

    # ── Write .env.example ───────────────────────────────────────────────────
    env_example_path = target / ".env.example"
    if not env_example_path.exists() or args.overwrite:
        env_example_path.write_text(_ENV_EXAMPLE)
        if verbose:
            print("  created: .env.example")

    # ── Write .env with generated SECRET_KEY ─────────────────────────────────
    env_path = target / ".env"
    if not env_path.exists() or args.overwrite:
        secret_key = _get_random_secret_key()
        # Avoid leading '$' which triggers django-environ variable expansion
        while secret_key.startswith("$"):
            secret_key = _get_random_secret_key()

        env_content = _ENV_EXAMPLE.replace(
            "SECRET_KEY=change-me-to-a-random-string",
            f"SECRET_KEY={secret_key}",
        )
        env_path.write_text(env_content)
        if verbose:
            print("  created: .env (with generated SECRET_KEY)")

    # ── Make manage.py executable ────────────────────────────────────────────
    manage_py = target / "manage.py"
    if manage_py.exists():
        manage_py.chmod(manage_py.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)

    # ── Print next steps ─────────────────────────────────────────────────────
    if verbose:
        print(f"""
  ✓ machado project created at: {target}

  Next steps:
    1. cd {target}
    2. Edit .env — set DATABASE_URL with your PostgreSQL credentials
    3. python manage.py migrate
    4. python manage.py runserver

  Optional:
    • Run 'python manage.py rebuild_search_index' after loading data
    • See .env.example for all available settings
""")


if __name__ == "__main__":
    main()
