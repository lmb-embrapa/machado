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
