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

            and_facets = ['analyses']

            # the results of these facets will be united (union/or)
            for key, values in selected_facets.items():
                if key not in and_facets:
                    key += "_exact__in"
                    sqs &= self.searchqueryset.filter(**{key: values})

            # the results of these facets will be intersected (intersect/and)
            for key, values in selected_facets.items():
                if key in and_facets:
                    queries = [SQ(analyses_exact=Exact(value)) for value in values]
                    query = queries.pop()
                    for item in queries:
                        query &= item
                    sqs = sqs.filter(query)

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
