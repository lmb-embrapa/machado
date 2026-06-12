# Machado User Manual

**machado** provides users with a framework to store, search, and visualize biological data.

It is powered by [Django](https://www.djangoproject.com/) and contains tools to interact with a [Chado](http://gmod.org/wiki/Chado_-_Getting_Started) database.

---

## Contents

1. [Installation](01-installation.md)
2. [Data Loading](02-data-loading.md)
   - [Ontologies](03-load-ontologies.md)
   - [Taxonomy](04-load-taxonomy.md)
   - [Organism](05-insert-organism.md)
   - [Publication](06-load-publication.md)
   - [FASTA](07-load-fasta.md)
   - [GFF](08-load-gff.md)
   - [Feature Additional Info](09-load-feature-annotation.md)
   - [BLAST](10-load-blast.md)
   - [InterProScan](11-load-interproscan.md)
   - [OrthoMCL](12-load-orthomcl.md)
   - [RNA-seq](13-load-rnaseq.md)
   - [Coexpression](14-load-coexpression.md)
   - [VCF](15-load-vcf.md)
3. [Visualization](16-visualization.md)
   - [Index and Search](17-index-search.md)
   - [Web Server](18-webserver.md)
   - [Customization](23-customization.md)
   - [JBrowse](19-jbrowse.md)
   - [Cache](20-cache.md)
4. [Diagrams](21-diagrams.md)
5. [Models](22-models.md)

---

## Technical Stack Documentation

For developer-oriented documentation covering the database schema, REST API, loaders internals, and CI/CD, see the [techstack/](techstack/) directory.
