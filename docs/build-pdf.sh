#!/usr/bin/env bash
# Rebuild docs/machado-manual.pdf from the markdown pages.
#
# Requires pandoc and a LaTeX engine:
#   sudo apt install pandoc texlive-latex-recommended \
#                    texlive-latex-extra texlive-fonts-recommended
#
# Run from anywhere; paths are resolved relative to this script.
set -euo pipefail

cd "$(dirname "$0")"

# Reading order, matching the contents list in index.md -- which is not the
# numeric order: customization (22) is grouped with the other visualization
# pages, before JBrowse (19).
PAGES=(
  index.md
  01-installation.md
  02-data-loading.md
  03-load-ontologies.md
  04-load-taxonomy.md
  05-insert-organism.md
  06-load-publication.md
  07-load-fasta.md
  08-load-gff.md
  09-load-feature-annotation.md
  10-load-blast.md
  11-load-interproscan.md
  12-load-orthomcl.md
  13-load-rnaseq.md
  14-load-coexpression.md
  15-load-vcf.md
  16-visualization.md
  17-index-search.md
  18-webserver.md
  22-customization.md
  19-jbrowse.md
  20-diagrams.md
  21-models.md
)

for page in "${PAGES[@]}"; do
  [ -f "$page" ] || { echo "missing page: $page" >&2; exit 1; }
done

# Every .md here should be in the list above; a page added without being
# listed would silently never reach the PDF.
for page in [0-9][0-9]-*.md index.md; do
  case " ${PAGES[*]} " in
    *" $page "*) ;;
    *) echo "page not listed in build-pdf.sh: $page" >&2; exit 1 ;;
  esac
done

# No --toc and no title metadata: index.md already opens with the manual's
# title and its own Contents list, and this matches how the committed PDF was
# built.
pandoc "${PAGES[@]}" \
  --resource-path=.:images \
  --include-in-header=pdf-header.tex \
  -o machado-manual.pdf

echo "wrote docs/machado-manual.pdf"
