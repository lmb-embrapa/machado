# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Search views — PostgreSQL full-text search."""

from django.db import connection
from django.db.models import Count
from django.views.generic import ListView

from machado.forms import FeatureSearchForm
from machado.models import Featureprop
from machado.models import FeatureSearchIndex

FACET_FIELDS = {
    "organism": "Filter by organism (gene, mRNA, polypeptide)",
    "so_term": "Filter by sequence ontology term",
    "orthology": "Filter by orthology (polypeptide)",
    "coexpression": "Filter by coexpression (mRNA)",
    "orthologs_coexpression": "Filter by coexpression in orthologous groups members (polypeptide)",
    "analyses": "Filter by blast and inteproscan (polypeptide)",
    "biomaterial": "Filter by RNA-seq biomaterial (mRNA)",
    "treatment": "Filter by RNA-Seq sample (mRNA)",
    "orthologous_group": "Filter by the orthologous group ID",
    "coexpression_group": "Filter by the coexpression group ID",
    "doi": "Filter by related publications (gene, mRNA, polypeptide)",
}

# Fields stored as JSON arrays — need special aggregation
_ARRAY_FACET_FIELDS = {
    "analyses",
    "biomaterial",
    "treatment",
    "doi",
    "orthologs_coexpression",
}

# Scalar facet fields (simple GROUP BY)
_SCALAR_FACET_FIELDS = {k for k in FACET_FIELDS if k not in _ARRAY_FACET_FIELDS}


class FeatureSearchView(ListView):
    """Faceted search view backed by PostgreSQL FTS."""

    model = FeatureSearchIndex
    template_name = "search_result.html"
    context_object_name = "object_list"
    paginate_by = 50

    def get_queryset(self):
        """Build the filtered search queryset."""
        form = FeatureSearchForm(self.request.GET)
        selected_facets = self.request.GET.getlist("selected_facets")

        if form.is_valid():
            qs = form.search(selected_facets=selected_facets)
        else:
            qs = FeatureSearchIndex.objects.none()

        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            from machado.models import Organism

            private_orgs = Organism.objects.filter(
                Organismprop_organism_Organism__type__name="is_public",
                Organismprop_organism_Organism__type__cv__name="organism_property",
                Organismprop_organism_Organism__value="false",
            )
            qs = qs.exclude(feature__organism__in=private_orgs)

        # Ordering
        order_by = self.request.GET.get("order_by", "uniquename")
        q = self.request.GET.get("q", "").strip()
        if q and not self.request.GET.get("order_by"):
            # default to relevance when searching
            qs = qs.order_by("-rank", "uniquename")
        else:
            qs = qs.order_by(order_by)

        # Per-page records
        if self.request.GET.get("records"):
            try:
                self.paginate_by = int(self.request.GET["records"])
            except (ValueError, TypeError):
                pass

        # cache for facet computation in get_context_data
        self._queryset_for_facets = qs
        return qs

    def get_context_data(self, **kwargs):
        """Inject facet counts and metadata into the template context."""
        context = super().get_context_data(**kwargs)
        qs = self._queryset_for_facets

        # ── Compute facets ───────────────────────────────────────────────
        facets = {}
        for field in FACET_FIELDS:
            if field in _ARRAY_FACET_FIELDS:
                facets[field] = self._compute_array_facet(qs, field)
            else:
                counts = (
                    qs.values(field)
                    .annotate(count=Count("pk"))
                    .filter(count__gt=0)
                    .order_by(field)[:100]
                )
                facets[field] = [
                    (row[field], row["count"])
                    for row in counts
                    if row[field] is not None
                ]

        selected_facets = self.request.GET.getlist("selected_facets")
        selected_facets_fields = [f.split(":")[0] for f in selected_facets]

        so_term_count = sum(1 for f in selected_facets if f.startswith("so_term:"))

        context["facets"] = {"fields": facets}
        context["facet_fields_order"] = list(FACET_FIELDS.keys())
        context["facet_fields_desc"] = FACET_FIELDS
        context["selected_facets"] = selected_facets
        context["selected_facets_fields"] = selected_facets_fields
        context["so_term_count"] = so_term_count
        context["query"] = self.request.GET.get("q", "")

        context["orthologs"] = Featureprop.objects.filter(
            type__name="orthologous group", type__cv__name="feature_property"
        ).exists()

        context["coexp_groups"] = Featureprop.objects.filter(
            type__name="coexpression group", type__cv__name="feature_property"
        ).exists()

        return context

    @staticmethod
    def _compute_array_facet(qs, field):
        """Unnest JSON arrays and count occurrences via raw SQL."""
        # Build a subquery using the PKs from the filtered queryset
        pks = qs.values_list("pk", flat=True)
        if not pks.exists():
            return []

        sql = """
            SELECT val, COUNT(*) AS cnt
            FROM machado_featuresearchindex,
                 jsonb_array_elements_text({field}) AS val
            WHERE feature_id IN (
                SELECT feature_id FROM machado_featuresearchindex
                WHERE feature_id = ANY(%s)
            )
            GROUP BY val
            ORDER BY val
            LIMIT 100
        """.format(field=field)

        pk_list = list(pks[:10000])  # cap to avoid oversized IN clause
        with connection.cursor() as cursor:
            cursor.execute(sql, [pk_list])
            return [(row[0], row[1]) for row in cursor.fetchall()]


class FeatureSearchExportView(ListView):
    """Export search results in TSV or FASTA format."""

    model = FeatureSearchIndex
    template_name = "search_result.out"
    context_object_name = "object_list"
    paginate_by = None  # no pagination for exports
    content_type = "text"

    def get_queryset(self):
        """Build the filtered search queryset (unpaginated)."""
        form = FeatureSearchForm(self.request.GET)
        selected_facets = self.request.GET.getlist("selected_facets")

        if form.is_valid():
            qs = form.search(selected_facets=selected_facets)
        else:
            qs = FeatureSearchIndex.objects.none()

        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            from machado.models import Organism

            private_orgs = Organism.objects.filter(
                Organismprop_organism_Organism__type__name="is_public",
                Organismprop_organism_Organism__type__cv__name="organism_property",
                Organismprop_organism_Organism__value="false",
            )
            qs = qs.exclude(feature__organism__in=private_orgs)

        order_by = self.request.GET.get("order_by", "uniquename")
        return qs.order_by(order_by)

    def get_context_data(self, **kwargs):
        """Add export format to context."""
        context = super().get_context_data(**kwargs)
        export_format = self.request.GET.get("export", "tsv")
        if export_format not in ("tsv", "fasta"):
            export_format = "tsv"
        self.file_format = export_format
        context["file_format"] = export_format
        return context

    def dispatch(self, *args, **kwargs):
        """Set Content-Disposition header for download."""
        response = super().dispatch(*args, **kwargs)
        filename = "machado_search_results.{}".format(self.file_format)
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        return response
