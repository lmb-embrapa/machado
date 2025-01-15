# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from django.conf import settings
from django.urls import include, path, re_path
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from machado.api.views import read as readView


router = routers.SimpleRouter(trailing_slash=False)

router.register(
    "jbrowse/stats/global", readView.JBrowseGlobalViewSet, basename="jbrowse_global"
)
router.register(
    r"jbrowse/features/(?P<refseq>.+)",
    readView.JBrowseFeatureViewSet,
    basename="jbrowse_features",
)
router.register(r"jbrowse/names", readView.JBrowseNamesViewSet, basename="jbrowse_names")
router.register(
    r"jbrowse/refSeqs.json", readView.JBrowseRefSeqsViewSet, basename="jbrowse_refseqs"
)
router.register(r"autocomplete", readView.autocompleteViewSet, basename="autocomplete")

router.register(r"organism/id", readView.OrganismIDViewSet, basename="organism_id")
router.register(r"organism/list", readView.OrganismListViewSet, basename="organism_list")
router.register(r"feature/id", readView.FeatureIDViewSet, basename="feature_id")
router.register(
    r"feature/ontology/(?P<feature_id>\d+)",
    readView.FeatureOntologyViewSet,
    basename="feature_ontology",
)

router.register(
    r"feature/ortholog/(?P<feature_id>\d+)",
    readView.FeatureOrthologViewSet,
    basename="feature_ortholog",
)
router.register(
    r"feature/proteinmatches/(?P<feature_id>\d+)",
    readView.FeatureProteinMatchesViewSet,
    basename="feature_proteinmatches",
)
router.register(
    r"feature/expression/(?P<feature_id>\d+)",
    readView.FeatureExpressionViewSet,
    basename="feature_expression",
)
router.register(
    r"feature/coexpression/(?P<feature_id>\d+)",
    readView.FeatureCoexpressionViewSet,
    basename="feature_coexpression",
)
router.register(
    r"feature/info/(?P<feature_id>\d+)",
    readView.FeatureInfoViewSet,
    basename="feature_info",
)
router.register(
    r"feature/location/(?P<feature_id>\d+)",
    readView.FeatureLocationViewSet,
    basename="feature_location",
)
router.register(
    r"feature/publication/(?P<feature_id>\d+)",
    readView.FeaturePublicationViewSet,
    basename="feature_publication",
)
router.register(
    r"feature/sequence/(?P<feature_id>\d+)",
    readView.FeatureSequenceViewSet,
    basename="feature_sequence",
)
router.register(
    r"feature/similarity/(?P<feature_id>\d+)",
    readView.FeatureSimilarityViewSet,
    basename="feature_similarity",
)


baseurl = None
if hasattr(settings, "MACHADO_URL"):
    baseurl = "{}/api/".format(settings.MACHADO_URL)

schema_view = get_schema_view(
    openapi.Info(title="machado API", default_version="v1"),
    url=baseurl,
    public=True,
)

urlpatterns = [
    path("", include(router.urls)),
    re_path(
        r"^(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"
    ),
]
