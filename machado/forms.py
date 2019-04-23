# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Search forms."""

from haystack.forms import FacetedSearchForm
from haystack.inputs import Exact
from haystack.query import SQ


class FeatureSearchForm(FacetedSearchForm):
    """Search form."""

    def search(self):
        """Search."""
        # sqs = super(FeatureSearchForm, self).search()
        q = self.cleaned_data.get("q")
        sqs = self.searchqueryset

        if not self.is_valid():
            return self.no_query_found()

        selected_facets = dict()
        if "selected_facets" in self.data:
            for facet in self.data.getlist("selected_facets"):
                facet_field, facet_query = facet.split(":")
                selected_facets.setdefault(facet_field, []).append(facet_query)

            for key, values in selected_facets.items():
                if key == "analyses":
                    for item in values:
                        key += "_exact__in"
                        sqs &= self.searchqueryset.filter_and(**{key: values})
                else:
                    key += "_exact__in"
                    sqs &= self.searchqueryset.filter_and(**{key: values})

        if q == "":
            return sqs.load_all()

        result = sqs.filter(
            SQ(uniquename_exact=Exact(q))
            | SQ(name_exact=Exact(q))
            | SQ(organism_exact=Exact(q))
        )

        for i in q.split():
            result |= sqs.filter(text__startswith=i)

        return result
