# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.conf import settings
from django.urls import re_path, path, include

from machado.views import common

try:
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 60 * 60

from machado.views import feature, search, autocomplete, jbrowse, loader

urlpatterns = [
    re_path(
        r"^autocomplete/$",
        autocomplete.AutocompleteView.as_view(),
        name="autocomplete_html",
    ),
    re_path(
        r"^api/jbrowse/stats/global$", jbrowse.jbrowse_global, name="jbrowse_global"
    ),
    re_path(r"^api/jbrowse/names$", jbrowse.jbrowse_names, name="jbrowse_names"),
    re_path(
        r"^api/jbrowse/refSeqs.json$", jbrowse.jbrowse_refseqs, name="jbrowse_refseqs"
    ),
    re_path(
        r"^api/jbrowse/features/(?P<refseq>.+)$",
        jbrowse.jbrowse_features,
        name="jbrowse_features",
    ),
    re_path(
        r"^feature/$",
        feature.FeatureView.as_view(),
        name="feature",
    ),
    re_path(
        r"^data/$",
        common.DataSummaryView.as_view(),
        name="data_numbers",
    ),
    re_path(
        r"^find/$",
        search.FeatureSearchView.as_view(),
        name="feature_search",
    ),
    re_path(
        r"^export/$",
        search.FeatureSearchExportView.as_view(),
        name="feature_search_export",
    ),
    path("loader/accounts/", include("django.contrib.auth.urls")),
    path("loader/", loader.DashboardView.as_view(), name="loader_dashboard"),
    path("loader/history/", loader.HistoryListView.as_view(), name="loader_history"),
    path(
        "loader/command/<str:command_name>/",
        loader.CommandFormView.as_view(),
        name="loader_command_form",
    ),
    path(
        "loader/permissions/",
        loader.OrganismPermissionsView.as_view(),
        name="loader_permissions",
    ),
    re_path(r"^$", common.HomeView.as_view(), name="home"),
]
