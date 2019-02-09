# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Search views."""

from haystack.generic_views import SearchView
from machado.forms import FeatureSearchForm


class FeatureSearchView(SearchView):
    """Search view."""

    form_class = FeatureSearchForm
    template_name = 'search_result.html'
    paginate_by = 10
    context_object_name = 'object_list'

    def get_context_data(self, *args, **kwargs):
        """Get context data."""
        context = super(FeatureSearchView, self).get_context_data(*args,
                                                                  **kwargs)
        print(context)
        return context
