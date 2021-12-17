# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.conf import settings
from django.urls import include, re_path
from django.views.decorators.cache import cache_page

from machado.views import common

try:
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 60 * 60

if "haystack" in settings.INSTALLED_APPS:
    from machado.views import feature, search

    urlpatterns = [
        re_path(r"api/", include("machado.api.urls"), name="api"),
        re_path(
            r"feature/",
            cache_page(CACHE_TIMEOUT)(feature.FeatureView.as_view()),
            name="feature",
        ),
        re_path(
            r"data/",
            cache_page(CACHE_TIMEOUT)(common.DataSummaryView.as_view()),
            name="data_numbers",
        ),
        re_path(
            r"find/",
            cache_page(CACHE_TIMEOUT)(search.FeatureSearchView.as_view()),
            name="feature_search",
        ),
        re_path(
            r"export/",
            cache_page(CACHE_TIMEOUT)(search.FeatureSearchExportView.as_view()),
            name="feature_search_export",
        ),
        re_path(
            r"^$", cache_page(CACHE_TIMEOUT)(common.HomeView.as_view()), name="home"
        ),
    ]
else:
    urlpatterns = [
        re_path(
            r"^$", cache_page(CACHE_TIMEOUT)(common.CongratsView.as_view()), name="home"
        )
    ]
