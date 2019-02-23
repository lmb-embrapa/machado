# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Search forms."""

from haystack.forms import FacetedSearchForm
from haystack.inputs import AutoQuery, Exact
from haystack.query import SQ


class FeatureSearchForm(FacetedSearchForm):
    """Search form."""

    def search(self):
        """Search."""
        # sqs = super(FeatureSearchForm, self).search()
        q = self.cleaned_data.get('q')
        sqs = self.searchqueryset

        if not self.is_valid():
            return self.no_query_found()

        if 'selected_facets' in self.data:
            for facet in self.data.getlist('selected_facets'):
                facet_field, facet_query = facet.split(':')
                sqs = sqs.filter(**{facet_field: Exact(facet_query)})
                # narrowing did not work
                # sqs = sqs.narrow(facet)

        if q == '':
            return sqs.load_all()

        # sqs = sqs.narrow(u'organism_exact:%s' % q)

        q = self.cleaned_data['q']
        sqs = sqs.filter(
            SQ(uniquename_exact=Exact(q)) |
            SQ(name_exact=Exact(q)) |
            SQ(text=AutoQuery(q)))
        return sqs
