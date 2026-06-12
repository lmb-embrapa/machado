# Customization Guide

Machado Genomics provides built-in options to customize the landing page and add Release Notes. This makes it simple for users to adapt each installation to specific biological species or data portals without editing the source code.

---

## 1. Landing Page Customization

You can customize almost all titles, descriptions, icons, and texts on the homepage by setting environment variables in your `.env` file (or configuring them directly in your system/container environment).

### How to Hide Features or Steps
If your installation does not require all feature cards or all "How it works" steps, you can **hide** any card or step by setting its corresponding `_TITLE` variable to an empty string (e.g. `MACHADO_FEATURE3_TITLE=""` or `MACHADO_STEP3_TITLE=""`).

### Settings Reference

Below is a complete reference of the 19 customizable settings, their corresponding environment variables, and their default values:

| Environment Variable | Description | Default Value |
| :--- | :--- | :--- |
| **Site-wide Settings** | | |
| `MACHADO_SITE_TITLE` | Browser tab title, navbar brand, and footer title. | `"Machado Genomics"` |
| `MACHADO_SITE_DESCRIPTION` | HTML meta description tag for search engine optimization (SEO). | `"Machado Genomics — biological data management"` |
| **Hero Section** | | |
| `MACHADO_HERO_TITLE` | Main heading in the landing page hero banner. | `"Genomics Data Management Portal"` |
| `MACHADO_HERO_SUBTITLE` | Paragraph text shown below the main heading in the hero banner. | `"Explore, search, and visualize genomics sequences, annotations, and publications stored in the Chado database."` |
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
