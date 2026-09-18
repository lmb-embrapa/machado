# Changelog

All notable changes to machado are recorded here. Releases before 0.9.0 are
summarized from their [GitHub release notes](https://github.com/lmb-embrapa/machado/releases).

## Unreleased

### Breaking

- **machado no longer configures your project for you.** `machado/settings.py`,
  which used to mutate `django.conf.settings` from `AppConfig.ready()`
  (`patch_all()`), is deleted. The settings it used to set —
  `USE_THOUSAND_SEPARATOR`, `APPEND_SLASH`, `USE_TZ`, the proxy-header
  settings, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`, and
  machado's URL inclusion — must now be declared explicitly in the project's
  own `settings.py`/`urls.py`. Eight new system checks, `machado.E001`
  through `machado.E008`, report each missing piece with a hint that names
  the fix. These checks are registered untagged, so they run before **every**
  management command — `migrate`, `collectstatic`, `runserver`, and the
  rest — not just `manage.py check`: an existing deployment that upgrades
  without updating its settings will have every management command abort
  until the settings are fixed. A project created with the current
  `machado-startproject` already has everything it needs. See the
  "Upgrading from a version before the settings change" section of
  [docs/01-installation.md](docs/01-installation.md).
- `SWAGGER_SETTINGS` is no longer set anywhere; nothing in machado read it.

### Changed

- **`machado/decorators.py` replaced by `machado/mixins.py`.** The
  `setattr`-based method injection onto `Feature`, `Pub` and `Organism` is
  gone; `FeatureMixin`, `PubMixin` and `OrganismMixin` provide the same
  methods through plain inheritance instead. The models already inherit from
  them, so most projects need no change; a project that imported
  `machado.decorators` directly should import `machado.mixins` instead.
- **Display and DOI resolution consolidated into `machado/display.py`.** The
  feature page (via `FeatureMixin`) and the search index (via
  `machado.searchindex.prefetch_chunk`) used to carry two hand-synchronised
  copies of the display-fallback and DOI-resolution logic; both now call the
  same functions in `machado.display`, so the two can no longer disagree
  about a feature's display value or its DOIs.

## 0.9.0 — 2026-09-14

### Added

- **Web interface for data loading.** A password-protected portal replaces
  running every loader by hand on the server: a dashboard, a form per loader
  command, and a history page. The history model records each run's PID,
  stdout, stderr, and finish time, so a background load can be followed from
  the browser. `rebuild_search_index` exposes its `--resume` option there too.
- **Public/private organisms.** A permissions panel toggles an organism's
  visibility; anonymous visitors no longer see features belonging to organisms
  marked private, on either the search page or the data summary.
- **Landing page customization.** 29 `MACHADO_*` settings drive the hero,
  feature cards, How It Works steps, acknowledgements, and footer, so an
  installation can be rebranded from `.env` without touching templates. A
  selectable accent color and an optional release-notes accordion
  (`release_notes.json`) come with it. See
  [docs/22-customization.md](docs/22-customization.md).
- **Page cache.** The search page (`/find/`) and the data summary (`/data/`)
  are cached whole on disk, keyed separately for anonymous and logged-in
  visitors. Entries have no expiry; they are cleared when the search index is
  rebuilt and when an organism's visibility changes. A startup check
  (`machado.W001`) reports an unusable cache directory, and a failing cache
  backend degrades a page to slow rather than to a 500.
- `MACHADO_SHOW_STATS` hides the landing page's Organisms / Genomic Features /
  Ingestion Formats panel, and skips the two table scans that back it.
- Gzipped FASTA input in the Load FASTA form, and `TIME_ZONE`, `URL_PREFIX`,
  and CSRF settings in the generated `.env`.

### Changed

- **Search index rebuild is batched.** Features are indexed in chunks, each
  issuing a fixed small number of queries for the related data it needs and
  then bulk-inserting, instead of per-feature lookups. `--batch-size` tunes
  the chunk, and `--resume` continues an interrupted run.
- `search_vector` is maintained as a PostgreSQL generated column rather than
  being recomputed on write.
- The DOI facet shows publication titles instead of raw DOIs, with
  BibTeX/LaTeX markup stripped.
- Facet cards offering only one option are hidden.
- Loader error handling was reworked across the loaders library and the
  management commands, with clearer messages on bad input.

### Fixed

- **Faceted search was both wrong and slow.** Array-backed facets (analyses,
  DOI, biomaterial, treatment, orthologs/coexpression) undercounted past
  10,000 rows; selecting one facet discarded earlier selections; boolean facet
  values of differing case returned a 500; and a comment in the facet form
  rendered into the page.
- The data summary and landing page no longer count the `multispecies`
  placeholder organism.
- `create_point(bigint, bigint)` failure loading the Chado schema under
  psycopg 3.
- Django command discovery no longer picks up `_base.py` as a command.
- `tqdm` progress output is no longer stored in the history record's stderr,
  and the progress bar writes to the command's own stdout.
- The Load FASTA form sends `--nosequence` as a bare flag, which is what
  argparse expects for a `store_true` argument.
- Deterministic tie-breaking when a publication carries multiple DOIs, and
  reproducible ordering of autocomplete keywords.

### Performance

- Feature page: the decorator helpers that traverse relations now use
  `select_related`, compute annotations and DOIs in one shared traversal,
  resolve the display fallback chain in a single query, and cache
  `Organism.is_public` per instance (invalidated on change). The `Pub.get_doi`
  N+1 on the permissions page is gone.
- Indexes added on `FeatureSearchIndex.orthology` and `.coexpression`, and on
  the non-empty rows of the sparse array facets.
- Search and facet queries no longer join `feature`/`organism`, and the
  organism exclusion is skipped when it cannot match.

### Infrastructure

- CI runs `collectstatic` before the test suite; Ubuntu, Python, Node (20.x),
  and psycopg versions bumped; the Chado schema SQL is shipped gzipped.

## 0.8.0 — 2026-05-13

Asynchronous card loading via htmx. `django-rest-framework` replaced by native
Django views, and search migrated from Elasticsearch to PostgreSQL. The API was
trimmed to the four endpoints JBrowse requires.

## 0.7.0 — 2026-05-07

Installation refactored towards a simpler setup, with documentation updated to
match.

## 0.6.0 — 2026-05-06

New API endpoints. Data loading refactored so every command logs to the history
model, enabling background loads. `load_orthologs` handles OrthoMCL files, and
dbxref URLs are rendered as links.

## 0.5.0 — 2023-10-18

Features may share an identifier across different organisms. New helper to
retrieve a cvterm by name or synonym. Fixed the Sequence Ontology term
`contained in`, obsolete in favour of `located in`.

## 0.4.0 — 2022-08-18

API examples read from `settings.py`. Feature page loads expression data into a
dynamic table. JBrowse SNV tracks. Search index covers feature names, dbxrefs,
and overlapping feature uniquenames. Configurable `valid_types`, a dedicated
feature-attributes class, and a DOI option for `load_feature_annotation`.

## 0.3.0 — 2020-09-04

API moved from coreAPI to OpenAPI, documented with Swagger. New
`MACHADO_JBROWSE_TRACKS` setting. Feature pages show dbxrefs and NCBI protein
links; flake8 joined the test suite.

## 0.2.1 — 2020-05-13

Search results page optimized to avoid hitting the database, with an organism
column, sorting, and a configurable record count. New APIs for sequences,
orthologs, and publications. `load_gff` loads relationships using threads.

## 0.1.1 — 2020-02-12

First published release on [PyPI](https://pypi.org/project/machado/).
