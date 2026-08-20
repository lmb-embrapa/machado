# Customization Guide

Machado Genomics provides built-in options to customize the landing page and add Release Notes. This makes it simple for users to adapt each installation to specific biological species or data portals without editing the source code.

---

## 1. Landing Page Customization

You can customize almost all titles, descriptions, icons, and texts on the homepage by setting environment variables in your `.env` file (or configuring them directly in your system/container environment).

### How to Hide Optional Sections
If your installation does not require all feature cards or all "How it works" steps, you can **hide** any card or step by setting its corresponding `_TITLE` variable to an empty string (e.g. `MACHADO_FEATURE3_TITLE=""` or `MACHADO_STEP3_TITLE=""`).

The same pattern applies to several whole sections, which are hidden automatically when their controlling setting is empty:

- The "Key Features & Capabilities" heading and subtitle are hidden when `MACHADO_FEATURES_TITLE` is set to an empty string.
- The Acknowledgements section is hidden unless `MACHADO_ACKNOWLEDGEMENTS_TEXT` is set — it is **empty by default**, so this section does not appear at all until you configure it.
- The footer's extra text block is hidden unless `MACHADO_FOOTER_TEXT` is set — it is also **empty by default**.

### Settings Reference

Below is a complete reference of the 26 customizable settings, their corresponding environment variables, and their default values:

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
| **Feature Card 2** | | |
| `MACHADO_FEATURE2_TITLE` | Title of the second feature card. | `"PostgreSQL Faceted Search"` |
| `MACHADO_FEATURE2_TEXT` | Description of the second feature. | `"Execute complex queries powered by PostgreSQL full-text search. Filter features by organism, sequence ontology terms, orthology, coexpression groups, and related publications."` |
| `MACHADO_FEATURE2_ICON` | FontAwesome 5 CSS class name for the card icon. | `"fas fa-search"` |
| **Feature Card 3** | | |
| `MACHADO_FEATURE3_TITLE` | Title of the third feature card. | `"Genome Browser Integration"` |
| `MACHADO_FEATURE3_TEXT` | Description of the third feature. | `"Interactive visual analysis of features. Machado Genomics API delivers data directly to the embedded JBrowse genome browser for sequence and annotation alignments."` |
| `MACHADO_FEATURE3_ICON` | FontAwesome 5 CSS class name for the card icon. | `"fas fa-align-left"` |
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
| `MACHADO_ACKNOWLEDGEMENTS_TEXT` | Body text for the Acknowledgements section. This section is **hidden from the page entirely** unless this setting is non-empty; it is empty by default. | `""` |
| **Footer** | | |
| `MACHADO_FOOTER_COPYRIGHT` | Copyright line shown in the footer. | `"© 2026 Embrapa. All rights reserved."` |
| `MACHADO_FOOTER_TEXT` | Optional extra text block shown above the footer's copyright/attribution row. Hidden entirely unless set; empty by default. | `""` |

The footer's "Powered by Machado Genomics" line is a hardcoded literal and is **not** configurable via any setting — it deliberately does not reflect `MACHADO_SITE_TITLE` or any other setting, so renaming a site instance never rewords it.

> **Upgrading an existing project:** the six settings `MACHADO_FEATURES_TITLE`, `MACHADO_FEATURES_SUBTITLE`, `MACHADO_ACKNOWLEDGEMENTS_TITLE`, `MACHADO_ACKNOWLEDGEMENTS_TEXT`, `MACHADO_FOOTER_COPYRIGHT`, and `MACHADO_FOOTER_TEXT` were added to the project template after some existing projects were generated (and `MACHADO_ACCENT_COLOR` may be missing too, if your project predates that setting). If your `machadoproject/settings.py` predates one of these settings, setting the corresponding environment variable in your `.env` is a **silent no-op**: nothing reads it into a Django setting, so the page just falls back to the built-in default, with no error or warning. To use these settings in an existing project, add the matching `env(...)` lines to your own `machadoproject/settings.py` by hand, copying them from the "Landing page customization" section of `machado/project_template/machadoproject/settings.py` in the machado package. Regenerating the project from the template is **not** a safe shortcut — using `--overwrite` would clobber any customizations you have already made to that file.

---

## 2. Release Notes

A "Release Notes" section is dynamically displayed at the bottom of the landing page. It is structured as an accordion list using Bootstrap 4 where only the latest version note is expanded by default, and all previous versions are collapsed.

### Display Logic
- **Automatic Toggle**: If there is no `release_notes.json` file in your project root, the Release Notes section will be **completely hidden** from the landing page.
- **Accordion Style**: When a file is found, it renders as a card deck where clicking on a version header toggles its description. The first item in the list is always expanded on page load.
- **Caching**: For optimal performance, the Release Notes file is read and parsed **once at server startup**. If you modify `release_notes.json`, you must restart your web server (e.g. Apache, Gunicorn, or Django runserver) for the changes to take effect.

### Configuration Format

To define release notes, create a file named `release_notes.json` in your project's base directory (the directory containing `manage.py` and your `.env` file). The file must contain a JSON array of objects, each representing a release.

Here is an example format of a `release_notes.json` file:

```json
[
  {
    "version": "v1.2.0",
    "date": "2026-06-12",
    "description": "Added customizable landing page settings and a brand new Release Notes accordion section. Fixed JBrowse alignment offset issues."
  },
  {
    "version": "v1.1.0",
    "date": "2026-04-05",
    "description": "Improved PostgreSQL search performance and added full-text index triggers for faster multi-faceted query execution."
  },
  {
    "version": "v1.0.0",
    "date": "2026-01-10",
    "description": "Initial stable release of the Machado Genomics data portal framework with support for core GFF3, FASTA, and BLAST loaders."
  }
]
```
