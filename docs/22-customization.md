# Customization Guide

Machado Genomics provides built-in options to customize the landing page and add Release Notes. This makes it simple for users to adapt each installation to specific biological species or data portals without editing the source code.

---

## 1. Landing Page Customization

You can customize almost all titles, descriptions, icons, and texts on the homepage by setting environment variables in your `.env` file (or configuring them directly in your system/container environment).

### How to Hide Optional Sections
If your installation does not require all feature cards or all "How it works" steps, you can **hide** any card or step by setting its corresponding `_TITLE` variable to an empty string (e.g. `MACHADO_FEATURE3_TITLE=""` or `MACHADO_STEP3_TITLE=""`).

The same pattern applies to several whole sections, which are hidden automatically when their controlling setting is empty:

- The "Key Features & Capabilities" heading and subtitle are hidden when `MACHADO_FEATURES_TITLE` is set to an empty string.
- The "How It Works" heading, subtitle and body text are hidden when `MACHADO_HOWITWORKS_TITLE` is set to an empty string — the three step cards below it (`MACHADO_STEP1_TITLE` etc.) are unaffected and keep their own individual hide rule.
- The Acknowledgements section is hidden unless `MACHADO_ACKNOWLEDGEMENTS_TEXT` is set — it is **empty by default**, so this section does not appear at all until you configure it.
- The footer's extra text block is hidden unless `MACHADO_FOOTER_TEXT` is set — it is also **empty by default**.
- The live stats panel (Organisms / Genomic Features / Ingestion Formats) is hidden by setting `MACHADO_SHOW_STATS=False`. This one is a boolean rather than an empty title, because the panel has no title to blank out; turning it off also skips the two database counts behind it, which are unfiltered scans of the organism and feature tables.

### Settings Reference

Below is a complete reference of the 36 customizable settings, their corresponding environment variables, and their default values:

| Environment Variable | Description | Default Value |
| :--- | :--- | :--- |
| **Site-wide Settings** | | |
| `MACHADO_ACCENT_COLOR` | Accent color theme for the UI (accent-picker swatches in the navbar). Valid values: `steel`, `teal`, `sage`, `amber`, `graphite`, `ruby`, `indigo`, `emerald`, `coral`, `plum`. | `"steel"` |
| `MACHADO_SITE_TITLE` | Browser tab title and navbar brand. | `"Machado Genomics"` |
| `MACHADO_SITE_DESCRIPTION` | HTML meta description tag for search engine optimization (SEO). | `"Machado Genomics — biological data management"` |
| **Hero Section** | | |
| `MACHADO_HERO_TITLE` | Main heading in the landing page hero banner. | `"Genomics Data Management Portal"` |
| `MACHADO_HERO_SUBTITLE` | Paragraph text shown below the main heading in the hero banner. | `"Explore, search, and visualize genomics sequences, annotations, and publications stored in the Chado database."` |
| **Key Features Section** | | |
| `MACHADO_FEATURES_TITLE` | Heading above the feature cards. Setting this to an empty string hides the whole heading and subtitle. | `"Key Features & Capabilities"` |
| `MACHADO_FEATURES_SUBTITLE` | Subtitle text shown below the Key Features heading. | `"A comprehensive ecosystem designed for biological database curation and research."` |
| **Feature Card 1** | | |
| `MACHADO_FEATURE1_TITLE` | Title of the first feature card. | `"Multi-Format Data Loaders"` |
| `MACHADO_FEATURE1_TEXT` | Description of the first feature. | `"Ingest data seamlessly from standard bioinformatics formats including FASTA, GFF3, OBO, BibTeX, BLAST, InterProScan, and OrthoMCL directly into the Chado relational schema."` |
| `MACHADO_FEATURE1_ICON` | FontAwesome 5 CSS class name for the card icon. | `"fas fa-file-import"` |
| `MACHADO_FEATURE1_LINK_TEXT` | Wording of the call-to-action link at the bottom of the first card. | `"Read Documentation"` |
| `MACHADO_FEATURE1_LINK_URL` | Destination of that link. Leave empty to use the built-in route, the loader dashboard. | `""` (loader dashboard) |
| **Feature Card 2** | | |
| `MACHADO_FEATURE2_TITLE` | Title of the second feature card. | `"PostgreSQL Faceted Search"` |
| `MACHADO_FEATURE2_TEXT` | Description of the second feature. | `"Execute complex queries powered by PostgreSQL full-text search. Filter features by organism, sequence ontology terms, orthology, coexpression groups, and related publications."` |
| `MACHADO_FEATURE2_ICON` | FontAwesome 5 CSS class name for the card icon. | `"fas fa-search"` |
| `MACHADO_FEATURE2_LINK_TEXT` | Wording of the call-to-action link at the bottom of the second card. | `"Start Searching"` |
| `MACHADO_FEATURE2_LINK_URL` | Destination of that link. Leave empty to use the built-in route, the feature search. | `""` (feature search) |
| **Feature Card 3** | | |
| `MACHADO_FEATURE3_TITLE` | Title of the third feature card. | `"Genome Browser Integration"` |
| `MACHADO_FEATURE3_TEXT` | Description of the third feature. | `"Interactive visual analysis of features. Machado Genomics API delivers data directly to the embedded JBrowse genome browser for sequence and annotation alignments."` |
| `MACHADO_FEATURE3_ICON` | FontAwesome 5 CSS class name for the card icon. | `"fas fa-align-left"` |
| `MACHADO_FEATURE3_LINK_TEXT` | Wording of the call-to-action link at the bottom of the third card. | `"Browse Organisms"` |
| `MACHADO_FEATURE3_LINK_URL` | Destination of that link. Leave empty to use the built-in route, the data summary. | `""` (data summary) |
| **Live Stats Panel** | | |
| `MACHADO_SHOW_STATS` | Whether to show the stats panel below the feature cards. Set to `False` to hide all three cards and skip the two counts that back them. | `True` |
| **How It Works Heading** | | |
| `MACHADO_HOWITWORKS_TITLE` | Heading above the "How It Works" step cards. Setting this to an empty string hides the whole heading and subtitle, but not the step cards below it. | `"How Machado Genomics Operates"` |
| `MACHADO_HOWITWORKS_SUBTITLE` | Subtitle text shown below the How It Works heading. | `"From raw genomic files to interactive database search and visualization."` |
| `MACHADO_HOWITWORKS_TEXT` | Optional body paragraph below the subtitle. Accepts links and line breaks (see *Links and line breaks* below). Hidden when empty. | `""` |
| **Step 1 (How It Works)** | | |
| `MACHADO_STEP1_TITLE` | Title for step 1 of the platform overview. | `"Load Data"` |
| `MACHADO_STEP1_TEXT` | Explanation of how data loading works. | `"Administrators run commands or use data tools to load genomic files into the database."` |
| **Step 2 (How It Works)** | | |
| `MACHADO_STEP2_TITLE` | Title for step 2 of the platform overview. | `"Index & Query"` |
| `MACHADO_STEP2_TEXT` | Explanation of how searching works. | `"PostgreSQL full-text index updates automatically, enabling fast, multi-faceted searches across millions of features."` |
| **Step 3 (How It Works)** | | |
| `MACHADO_STEP3_TITLE` | Title for step 3 of the platform overview. | `"Discover"` |
| `MACHADO_STEP3_TEXT` | Explanation of how discovery/viewing works. | `"Users inspect features, view analysis results, download bulk data, and browse via JBrowse."` |
| **Acknowledgements Section (optional)** | | |
| `MACHADO_ACKNOWLEDGEMENTS_TITLE` | Heading for the Acknowledgements section. | `"Acknowledgements"` |
| `MACHADO_ACKNOWLEDGEMENTS_TEXT` | Body text for the Acknowledgements section. Accepts links and line breaks (see *Links and line breaks* below). This section is **hidden from the page entirely** unless this setting is non-empty; it is empty by default. | `""` |
| **Footer** | | |
| `MACHADO_FOOTER_COPYRIGHT` | Copyright line shown in the footer. | `"© 2026 Embrapa. All rights reserved."` |
| `MACHADO_FOOTER_TEXT` | Optional extra text block shown above the footer's copyright/attribution row. Hidden entirely unless set; empty by default. | `""` |

### Links and line breaks

Two settings — `MACHADO_HOWITWORKS_TEXT` and `MACHADO_ACKNOWLEDGEMENTS_TEXT` — are rendered as HTML rather than as plain text, so they can carry links out to a funding agency, a partner institution, or your own documentation. Every other setting in the table above is escaped and will show any markup you write literally.

A `.env` value is always a single line, so write a line break as the two characters `\n`:

```
MACHADO_ACKNOWLEDGEMENTS_TEXT=Funded by <a href="https://fapesp.br">FAPESP</a> grant 0000/00000-0.\nHosted by <a href="https://www.embrapa.br">Embrapa</a>.
```

That renders as two lines, each carrying a working link. A real newline works too, if you set the variable from something other than a `.env` file.

Because these two values are **not** escaped, whatever HTML you put in them reaches the page as-is. That is safe here because `.env` is written by whoever deploys the instance and is never reachable by a site visitor — but it does mean a stray `<` or an unclosed tag will break the page layout rather than show up as text.

### Feature card links

Each feature card ends with a call-to-action link whose wording and destination are configurable:

| Card | Default wording | Default destination |
| :--- | :--- | :--- |
| 1 | "Read Documentation" | the loader dashboard |
| 2 | "Start Searching" | the feature search, with an empty query |
| 3 | "Browse Organisms" | the data summary |

Leaving a `_LINK_URL` empty keeps the built-in destination, which is resolved from machado's own URL configuration and therefore stays correct under a `URL_PREFIX` sub-path deployment. Setting one replaces the destination with exactly the URL you give, so use an absolute URL when pointing off-site.

Card 1's link is shown to every visitor, signed in or not. Its default destination, the loader dashboard, requires a login, so an anonymous visitor who follows it lands on the login page and is returned to the dashboard afterwards. If your instance has no data-loading users, point `MACHADO_FEATURE1_LINK_URL` somewhere public instead — the machado manual, for example.

The footer's "Powered by Machado Genomics" line is a hardcoded literal and is **not** configurable via any setting — it deliberately does not reflect `MACHADO_SITE_TITLE` or any other setting, so renaming a site instance never rewords it.

Note also that `MACHADO_HOWITWORKS_TITLE` is a plain static setting, not linked to `MACHADO_SITE_TITLE` — overriding `MACHADO_SITE_TITLE` alone no longer changes the "How It Works" heading; set `MACHADO_HOWITWORKS_TITLE` explicitly if you want it to match.

> **Upgrading an existing project:** the fifteen settings `MACHADO_FEATURES_TITLE`, `MACHADO_FEATURES_SUBTITLE`, `MACHADO_HOWITWORKS_TITLE`, `MACHADO_HOWITWORKS_SUBTITLE`, `MACHADO_HOWITWORKS_TEXT`, `MACHADO_ACKNOWLEDGEMENTS_TITLE`, `MACHADO_ACKNOWLEDGEMENTS_TEXT`, `MACHADO_FOOTER_COPYRIGHT`, `MACHADO_FOOTER_TEXT`, and the six `MACHADO_FEATURE<n>_LINK_TEXT` / `MACHADO_FEATURE<n>_LINK_URL` pairs were added to the project template after some existing projects were generated (and `MACHADO_ACCENT_COLOR` may be missing too, if your project predates that setting). If your `machadoproject/settings.py` predates one of these settings, setting the corresponding environment variable in your `.env` is a **silent no-op**: nothing reads it into a Django setting, so the page just falls back to the built-in default, with no error or warning. To use these settings in an existing project, add the matching `env(...)` lines to your own `machadoproject/settings.py` by hand, copying them from the "Landing page customization" section of `machado/project_template/machadoproject/settings.py` in the machado package. Regenerating the project from the template is **not** a safe shortcut — using `--overwrite` would clobber any customizations you have already made to that file.

---

## 2. Release Notes

A "Release Notes" section is dynamically displayed at the bottom of the landing page. It is structured as an accordion list using Bootstrap 4 where only the latest version note is expanded by default, and all previous versions are collapsed.

### Display Logic
- **Automatic Toggle**: If there is no `release_notes.json` file in your project root, the Release Notes section will be **completely hidden** from the landing page.
- **Accordion Style**: When a file is found, it renders as a card deck where clicking on a version header toggles its description. The first item in the list is always expanded on page load.
- **Caching**: For optimal performance, the Release Notes file is read and parsed **once at server startup**. If you modify `release_notes.json`, you must restart your web server (e.g. Apache, Gunicorn, or Django runserver) for the changes to take effect.

### Configuration Format

To define release notes, create a file named `release_notes.json` in your project's base directory (the directory containing `manage.py` and your `.env` file). The file must contain a JSON array of objects, each representing a release.

Three keys are read from each object:

- `version` — written **without** a leading `v`. The landing page prepends one, so `"1.2.0"` renders as `v1.2.0` and `"v1.2.0"` would render as `vv1.2.0`.
- `date` — shown next to the version, as given. Any format you like.
- `description` — rendered as a single block of plain text. Markdown is not interpreted and line breaks are not preserved, so write one paragraph of prose rather than a bulleted list.

Entries appear in the order given, and the first is expanded on page load — so put the newest release first.

Here is an example format of a `release_notes.json` file:

```json
[
  {
    "version": "1.2.0",
    "date": "2026-06-12",
    "description": "Added customizable landing page settings and a brand new Release Notes accordion section. Fixed JBrowse alignment offset issues."
  },
  {
    "version": "1.1.0",
    "date": "2026-04-05",
    "description": "Improved PostgreSQL search performance and added full-text index triggers for faster multi-faceted query execution."
  },
  {
    "version": "1.0.0",
    "date": "2026-01-10",
    "description": "Initial stable release of the Machado Genomics data portal framework with support for core GFF3, FASTA, and BLAST loaders."
  }
]
```
