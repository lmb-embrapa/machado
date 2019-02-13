# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.core.exceptions import ImproperlyConfigured
from django.conf.urls import include, url

# Don't add pages if the haystack library is not installed and configured.
try:
    from machado.views import common, feature, search

    urlpatterns = [
        url(r'feature/', feature.FeatureView.as_view(), name='feature'),
        url(r'data/', common.CommonView.as_view(), name='data_numbers'),
        url(r'api/', include('machado.api.urls')),
        url(r'find/', search.FeatureSearchView.as_view(),
            name='feature_search'),
        url(r'^.*', common.HomeView.as_view(), name='home')
    ]
except ImproperlyConfigured as e:
    urlpatterns = list()
