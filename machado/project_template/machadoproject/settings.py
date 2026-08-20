"""
Django settings for machadoproject.

All configuration is read from environment variables via a .env file.
See .env.example for the full list of available settings.
"""

import os
from pathlib import Path

import environ

# ── Base directory ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Environment ──────────────────────────────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)
env.escape_proxy = True
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ── Core ─────────────────────────────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# When running multiple machado instances on the same domain (e.g. mounted at
# different Apache subpaths), set URL_PREFIX to this instance's mount path so
# session/CSRF cookies and client-side storage don't collide between instances.
URL_PREFIX = env("URL_PREFIX", default="")
if URL_PREFIX:
    SESSION_COOKIE_PATH = URL_PREFIX
    CSRF_COOKIE_PATH = URL_PREFIX

# ── Applications ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "machado",
]


# ── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ── URLs ─────────────────────────────────────────────────────────────────────
ROOT_URLCONF = "machadoproject.urls"

# ── Templates ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "machado.context_processors.machado_site",
            ],
        },
    },
]

# ── Database ─────────────────────────────────────────────────────────────────
DATABASES = {"default": env.db()}

# ── Internationalization ─────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = True

# ── Static files ─────────────────────────────────────────────────────────────
STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = env("STATIC_ROOT", default=str(BASE_DIR / "staticfiles"))
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ── Default primary key ─────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── WSGI ─────────────────────────────────────────────────────────────────────
WSGI_APPLICATION = "machadoproject.wsgi.application"

# ── machado settings ─────────────────────────────────────────────────────────
MACHADO_VALID_TYPES = env.list(
    "MACHADO_VALID_TYPES", default=["gene", "mRNA", "polypeptide"]
)
MACHADO_OVERLAPPING_FEATURES = env.list(
    "MACHADO_OVERLAPPING_FEATURES", default=["SNV", "QTL", "copy_number_variation"]
)

if env("MACHADO_JBROWSE_URL", default=None):
    MACHADO_JBROWSE_URL = env("MACHADO_JBROWSE_URL")

if env("MACHADO_JBROWSE_OFFSET", default=None):
    MACHADO_JBROWSE_OFFSET = env.int("MACHADO_JBROWSE_OFFSET")

if env("MACHADO_JBROWSE_TRACKS", default=None):
    MACHADO_JBROWSE_TRACKS = env("MACHADO_JBROWSE_TRACKS")

# ── Landing page customization ──────────────────────────────────────────────
# All values have sensible defaults — override only what you need.
# Available values: steel, teal, sage, amber, graphite, ruby, indigo,
# emerald, coral, plum (see the accent-picker swatches in base.html).
MACHADO_ACCENT_COLOR = env("MACHADO_ACCENT_COLOR", default="steel")
MACHADO_SITE_TITLE = env("MACHADO_SITE_TITLE", default="Machado Genomics")
MACHADO_SITE_DESCRIPTION = env(
    "MACHADO_SITE_DESCRIPTION",
    default="Machado Genomics \u2014 biological data management",
)
MACHADO_HERO_TITLE = env(
    "MACHADO_HERO_TITLE", default="Genomics Data Management Portal"
)
MACHADO_HERO_SUBTITLE = env(
    "MACHADO_HERO_SUBTITLE",
    default=(
        "Explore, search, and visualize genomics sequences, annotations, "
        "and publications stored in the Chado database."
    ),
)

# Feature cards (set title to empty string to hide a card)
MACHADO_FEATURE1_TITLE = env(
    "MACHADO_FEATURE1_TITLE", default="Multi-Format Data Loaders"
)
MACHADO_FEATURE1_TEXT = env(
    "MACHADO_FEATURE1_TEXT",
    default=(
        "Ingest data seamlessly from standard bioinformatics formats "
        "including FASTA, GFF3, OBO, BibTeX, BLAST, InterProScan, and "
        "OrthoMCL directly into the Chado relational schema."
    ),
)
MACHADO_FEATURE1_ICON = env("MACHADO_FEATURE1_ICON", default="fas fa-file-import")

MACHADO_FEATURE2_TITLE = env(
    "MACHADO_FEATURE2_TITLE", default="PostgreSQL Faceted Search"
)
MACHADO_FEATURE2_TEXT = env(
    "MACHADO_FEATURE2_TEXT",
    default=(
        "Execute complex queries powered by PostgreSQL full-text search. "
        "Filter features by organism, sequence ontology terms, orthology, "
        "coexpression groups, and related publications."
    ),
)
MACHADO_FEATURE2_ICON = env("MACHADO_FEATURE2_ICON", default="fas fa-search")

MACHADO_FEATURE3_TITLE = env(
    "MACHADO_FEATURE3_TITLE", default="Genome Browser Integration"
)
MACHADO_FEATURE3_TEXT = env(
    "MACHADO_FEATURE3_TEXT",
    default=(
        "Interactive visual analysis of features. Machado Genomics API "
        "delivers data directly to the embedded JBrowse genome browser "
        "for sequence and annotation alignments."
    ),
)
MACHADO_FEATURE3_ICON = env("MACHADO_FEATURE3_ICON", default="fas fa-align-left")

# How It Works heading (set title to empty string to hide the heading, not the steps)
MACHADO_HOWITWORKS_TITLE = env(
    "MACHADO_HOWITWORKS_TITLE", default="How Machado Genomics Operates"
)
MACHADO_HOWITWORKS_SUBTITLE = env(
    "MACHADO_HOWITWORKS_SUBTITLE",
    default=(
        "From raw genomic files to interactive database search and " "visualization."
    ),
)

# How-it-works steps (set title to empty string to hide a step)
MACHADO_STEP1_TITLE = env("MACHADO_STEP1_TITLE", default="Load Data")
MACHADO_STEP1_TEXT = env(
    "MACHADO_STEP1_TEXT",
    default=(
        "Administrators run commands or use data tools to load genomic "
        "files into the database."
    ),
)
MACHADO_STEP2_TITLE = env("MACHADO_STEP2_TITLE", default="Index & Query")
MACHADO_STEP2_TEXT = env(
    "MACHADO_STEP2_TEXT",
    default=(
        "PostgreSQL full-text index updates automatically, enabling fast, "
        "multi-faceted searches across millions of features."
    ),
)
MACHADO_STEP3_TITLE = env("MACHADO_STEP3_TITLE", default="Discover")
MACHADO_STEP3_TEXT = env(
    "MACHADO_STEP3_TEXT",
    default=(
        "Users inspect features, view analysis results, download bulk "
        "data, and browse via JBrowse."
    ),
)

# Key features section (set title to empty string to hide the section)
MACHADO_FEATURES_TITLE = env(
    "MACHADO_FEATURES_TITLE", default="Key Features & Capabilities"
)
MACHADO_FEATURES_SUBTITLE = env(
    "MACHADO_FEATURES_SUBTITLE",
    default=(
        "A comprehensive ecosystem designed for biological database "
        "curation and research."
    ),
)

# Acknowledgements (optional; set text to empty string to hide the section)
MACHADO_ACKNOWLEDGEMENTS_TITLE = env(
    "MACHADO_ACKNOWLEDGEMENTS_TITLE", default="Acknowledgements"
)
MACHADO_ACKNOWLEDGEMENTS_TEXT = env("MACHADO_ACKNOWLEDGEMENTS_TEXT", default="")

# Footer
MACHADO_FOOTER_COPYRIGHT = env(
    "MACHADO_FOOTER_COPYRIGHT", default="\u00a9 2026 Embrapa. All rights reserved."
)
MACHADO_FOOTER_TEXT = env("MACHADO_FOOTER_TEXT", default="")

# ── Email configuration ──────────────────────────────────────────────────────
if env("EMAIL_URL", default=None):
    email_config = env.email_url("EMAIL_URL")
    EMAIL_BACKEND = email_config.get("EMAIL_BACKEND")
    EMAIL_HOST = email_config.get("EMAIL_HOST")
    EMAIL_PORT = email_config.get("EMAIL_PORT")
    EMAIL_HOST_USER = email_config.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = email_config.get("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = email_config.get("EMAIL_USE_TLS")
    EMAIL_USE_SSL = email_config.get("EMAIL_USE_SSL")
