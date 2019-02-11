# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Forms."""

from haystack.forms import FacetedSearchForm


class FeatureSearchForm(FacetedSearchForm):
    """Feature search form."""

    def __init__(self, *args, **kwargs):
        """Init."""
        data = dict(kwargs.get("data", []))
        self.organisms = data.get('organism', [])
        self.so_terms = data.get('so_term', [])
        super(FeatureSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        """Search."""
        sqs = super(FeatureSearchForm, self).search()

        if self.organisms:
            query = None
            for organism in self.organisms:
                if query:
                    query += u' OR '
                else:
                    query = u''
                    query += u'"%s"' % sqs.query.clean(organism)
            sqs = sqs.narrow(u'organism_exact:%s' % query)

        if self.so_terms:
            query = None
            for so_term in self.so_terms:
                if query:
                    query += u' OR '
                else:
                    query = u''
                    query += u'"%s"' % sqs.query.clean(so_term)
            sqs = sqs.narrow(u'so_term_exact:%s' % query)

        return sqs
