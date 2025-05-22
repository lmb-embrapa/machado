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

from machado.api.views import read as readViews
from machado.api.views import load as loadViews


router = routers.SimpleRouter(trailing_slash=False)

# readViews

router.register(
    "jbrowse/stats/global", readViews.JBrowseGlobalViewSet, basename="jbrowse_global"
)
router.register(
    r"jbrowse/features/(?P<refseq>.+)",
    readViews.JBrowseFeatureViewSet,
    basename="jbrowse_features",
)
router.register(
    r"jbrowse/names", readViews.JBrowseNamesViewSet, basename="jbrowse_names"
)
router.register(
    r"jbrowse/refSeqs.json", readViews.JBrowseRefSeqsViewSet, basename="jbrowse_refseqs"
)
router.register(r"autocomplete", readViews.autocompleteViewSet, basename="autocomplete")

router.register(r"organism/id", readViews.OrganismIDViewSet, basename="organism_id")
router.register(
    r"organism/list", readViews.OrganismListViewSet, basename="organism_list"
)
router.register(r"feature/id", readViews.FeatureIDViewSet, basename="feature_id")
router.register(
    r"feature/ontology/(?P<feature_id>\d+)",
    readViews.FeatureOntologyViewSet,
    basename="feature_ontology",
)

router.register(
    r"feature/ortholog/(?P<feature_id>\d+)",
    readViews.FeatureOrthologViewSet,
    basename="feature_ortholog",
)
router.register(
    r"feature/proteinmatches/(?P<feature_id>\d+)",
    readViews.FeatureProteinMatchesViewSet,
    basename="feature_proteinmatches",
)
router.register(
    r"feature/expression/(?P<feature_id>\d+)",
    readViews.FeatureExpressionViewSet,
    basename="feature_expression",
)
router.register(
    r"feature/coexpression/(?P<feature_id>\d+)",
    readViews.FeatureCoexpressionViewSet,
    basename="feature_coexpression",
)
router.register(
    r"feature/info/(?P<feature_id>\d+)",
    readViews.FeatureInfoViewSet,
    basename="feature_info",
)
router.register(
    r"feature/location/(?P<feature_id>\d+)",
    readViews.FeatureLocationViewSet,
    basename="feature_location",
)
router.register(
    r"feature/publication/(?P<feature_id>\d+)",
    readViews.FeaturePublicationViewSet,
    basename="feature_publication",
)
router.register(
    r"feature/sequence/(?P<feature_id>\d+)",
    readViews.FeatureSequenceViewSet,
    basename="feature_sequence",
)
router.register(
    r"feature/similarity/(?P<feature_id>\d+)",
    readViews.FeatureSimilarityViewSet,
    basename="feature_similarity",
)

router.register(
    r'publications/load', 
    PublicationViewSet, 
    basename='publication-load'
)


# loadViews

router.register(
    r"load/organism", 
    loadViews.OrganismViewSet, 
    basename="load_organism")

router.register(
    r"load/relations_ontology",
    loadViews.RelationsOntologyViewSet,
    basename="load_relations_ontology")

router.register(r"history", readViews.HistoryListViewSet, basename="loads_history")

router.register(r"load/sequence_ontology",
    loadViews.SequenceOntologyViewSet,
    basename="load_sequence_ontology")

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
