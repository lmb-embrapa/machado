# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.urls import path
from django.conf.urls import include, url
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from machado.api import views


router = routers.SimpleRouter(trailing_slash=False)

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

router.register(
    r"feature/ortholog/(?P<feature_id>.+)",
    views.FeatureOrthologViewSet,
    basename="feature_ortholog",
)
router.register(
    r"feature/sequence/(?P<feature_id>.+)",
    views.FeatureSequenceViewSet,
    basename="feature_sequence",
)
router.register(
    r"feature/publication/(?P<feature_id>.+)",
    views.FeaturePublicationViewSet,
    basename="feature_publication",
)

schema_view = get_schema_view(
    openapi.Info(title="machado API", default_version="v1"), public=True
)

urlpatterns = [
    path("", include(router.urls)),
    url(
        r"^(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "jbrowse/stats/global",
        views.JBrowseGlobalViewSet.as_view(),
        name="jbrowse_global",
    ),
]
