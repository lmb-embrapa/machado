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
        sqs = super(FeatureSearchForm, self).search()
        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data.get('q') is None:
            return self.no_query_found()

        q = self.cleaned_data['q']
        sqs = sqs.filter(
            SQ(uniquename=Exact(q)) |
            SQ(name=Exact(q)) |
            SQ(text=AutoQuery(q)))
        return sqs
