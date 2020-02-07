# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.conf.urls import include, url
from rest_framework.documentation import include_docs_urls
from rest_framework_nested import routers

from machado.api import views

router = routers.SimpleRouter(trailing_slash=False)

router.register(
    r"jbrowse/stats/global", views.JBrowseGlobalViewSet, basename="jbrowse_global"
)
router.register(
    r"jbrowse/features/(?P<refseq>.+)",
    views.JBrowseFeatureViewSet,
    basename="jbrowse_features",
)
router.register(r"jbrowse/names", views.JBrowseNamesViewSet, basename="jbrowse_names")
router.register(
    r"jbrowse/refSeqs.json", views.JBrowseRefSeqsViewSet, basename="jbrowse_refseqs"
)
router.register(r"autocomplete", views.autocompleteViewSet, basename="autocomplete")
urlpatterns = [
    url(r"", include_docs_urls(title="machado API")),
    url(r"", include(router.urls)),
]
