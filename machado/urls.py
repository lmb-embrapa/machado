# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.conf import settings
from django.conf.urls import include, url
from django.views.decorators.cache import cache_page

from machado.views import common

try:
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 60 * 60

if "haystack" in settings.INSTALLED_APPS:
    from machado.views import feature, search

    urlpatterns = [
        url(
            r"api/",
            include("machado.api.urls")
        ),
        url(
            r"feature/",
            cache_page(CACHE_TIMEOUT)(feature.FeatureView.as_view()),
            name="feature",
        ),
        url(
            r"data/",
            cache_page(CACHE_TIMEOUT)(common.DataSummaryView.as_view()),
            name="data_numbers",
        ),
        url(
            r"find/",
            cache_page(CACHE_TIMEOUT)(search.FeatureSearchView.as_view()),
            name="feature_search",
        ),
        url(
            r"export/",
            cache_page(CACHE_TIMEOUT)(search.FeatureSearchExportView.as_view()),
            name="feature_search_export",
        ),
        url(r"^$", cache_page(CACHE_TIMEOUT)(common.HomeView.as_view()), name="home"),
    ]
else:
    urlpatterns = [
        url(
            r"^$", cache_page(CACHE_TIMEOUT)(common.CongratsView.as_view()), name="home"
        )
    ]
