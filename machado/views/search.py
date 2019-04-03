# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Search views."""

from haystack.generic_views import FacetedSearchView
from machado.forms import FeatureSearchForm
from machado.models import FeatureRelationship

FACET_FIELDS = ['organism', 'so_term', 'orthology', 'analyses']


class FeatureSearchView(FacetedSearchView):
    """Search view."""

    form_class = FeatureSearchForm
    facet_fields = FACET_FIELDS
    template_name = 'search_result.html'
    paginate_by = 25
    context_object_name = 'object_list'

    def get_queryset(self):
        """Get queryset."""
        queryset = super(FeatureSearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        return queryset

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super(FeatureSearchView, self).get_context_data(*args,
                                                                  **kwargs)
        selected_facets = list()
        selected_facets_fields = list()
        for facet in self.get_form_kwargs()['selected_facets']:
            facet_field, facet_query = facet.split(':')
            selected_facets_fields.append(facet_field)
            selected_facets.append(facet)

        context['facet_fields_order'] = FACET_FIELDS
        context['selected_facets'] = selected_facets
        context['selected_facets_fields'] = selected_facets_fields

        context['orthologs'] = FeatureRelationship.objects.filter(
            type__name='in orthology relationship with',
            type__cv__name='relationship').distinct("value").exists()

        return context
