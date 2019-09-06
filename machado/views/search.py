# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Search views."""

from haystack.generic_views import FacetedSearchView

from machado.forms import FeatureSearchForm
from machado.models import Featureprop

FACET_FIELDS = {
    "organism": "Filter by organism (gene, mRNA, polypeptide)",
    "so_term": "Filter by sequence ontology term",
    "orthology": "Filter by orthology (polypeptide)",
    "coexpression": "Filter by coexpression (mRNA)",
    "orthologs_coexpression": "Filter by coexpression in orthologous groups members (polypeptide)",
    "orthologs_biomaterial": "Filter by biomaterial in orthologous groups members (polypeptide)",
    "analyses": "Filter by blast and inteproscan (polypeptide)",
    "biomaterial": "Filter by RNA-seq biomaterial (mRNA)",
    "treatment": "Filter by RNA-Seq sample (mRNA)",
}


class FeatureSearchView(FacetedSearchView):
    """Search view."""

    form_class = FeatureSearchForm
    facet_fields = list(FACET_FIELDS.keys())
    template_name = "search_result.html"
    paginate_by = 50
    context_object_name = "object_list"

    def get_queryset(self, *args, **kwargs):
        """Get queryset."""
        qs = super(FeatureSearchView, self).get_queryset(*args, **kwargs)

        for field in self.facet_fields:
            qs = qs.facet(field, min_doc_count=0, size=100)
        return qs

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super(FeatureSearchView, self).get_context_data(*args, **kwargs)
        so_term_count = 0
        selected_facets = list()
        selected_facets_fields = list()
        for facet in self.get_form_kwargs()["selected_facets"]:
            facet_field, facet_query = facet.split(":")
            if facet_field == 'so_term':
                so_term_count += 1
            if facet_field not in ["orthologous_group", "coexpression_group"]:
                selected_facets_fields.append(facet_field)
                selected_facets.append(facet)

        context["so_term_count"] = so_term_count

        context["facet_fields_order"] = list(FACET_FIELDS.keys())
        context["facet_fields_desc"] = FACET_FIELDS
        context["selected_facets"] = selected_facets
        context["selected_facets_fields"] = selected_facets_fields

        context["orthologs"] = Featureprop.objects.filter(
            type__name="orthologous group", type__cv__name="feature_property"
        ).exists()

        context["coexp_groups"] = Featureprop.objects.filter(
            type__name="coexpression group", type__cv__name="feature_property"
        ).exists()

        return context


class FeatureSearchExportView(FacetedSearchView):
    """Export search results view."""

    form_class = FeatureSearchForm
    facet_fields = list(FACET_FIELDS.keys())
    template_name = "search_result.out"
    paginate_by = False
    context_object_name = "object_list"
    content_type = "text"

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super(FeatureSearchExportView, self).get_context_data(*args, **kwargs)

        if self.get_form_kwargs()["data"].get("export") in ["tsv", "fasta"]:
            file_format = self.get_form_kwargs()["data"].get("export")
        else:
            file_format = "tsv"

        self.file_format = file_format
        context["file_format"] = file_format

        return context

    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        response = super(FeatureSearchExportView, self).dispatch(*args, **kwargs)
        filename = "machado_search_results.{}".format(self.file_format)
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        return response
