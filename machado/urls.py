# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from machado import views
from django.conf.urls import include, url
from rest_framework_nested import routers
from rest_framework.documentation import include_docs_urls

router = routers.SimpleRouter()
router.register(r'analysis', views.AnalysisViewSet, base_name='analysis')
router.register(r'matches', views.MatchesViewSet,
                base_name='matches')
router.register(r'organism', views.OrganismViewSet, base_name='organism')
router.register(r'cv', views.CvViewSet, base_name='cv')
router.register(r'cvterm', views.CvtermViewSet, base_name='cvterm')
router.register(r'db', views.DbViewSet, base_name='db')
router.register(r'dbxref', views.DbxrefViewSet, base_name='dbxref')
router.register(r'chromosome', views.ChromosomeViewSet, base_name='chromosome')
router.register(r'scaffold', views.ScaffoldViewSet, base_name='scaffold')
router.register(r'gene', views.GeneViewSet, base_name='gene')
router.register(r'protein', views.ProteinViewSet, base_name='protein')

analysis_router = routers.NestedSimpleRouter(
    router, r'analysis', lookup='analysis')
analysis_router.register(r'matches', views.NestedMatchesViewSet)

cv_router = routers.NestedSimpleRouter(
    router, r'cv', lookup='cv')
cv_router.register(r'cvterm', views.NestedCvtermViewSet)

db_router = routers.NestedSimpleRouter(
    router, r'db', lookup='db')
db_router.register(r'dbxref', views.NestedDbxrefViewSet)

organism_router = routers.NestedSimpleRouter(
    router, r'organism', lookup='organism')
organism_router.register(r'chromosome', views.NestedChromosomeViewSet,
                         base_name='chromosome')
organism_router.register(r'scaffold', views.NestedScaffoldViewSet,
                         base_name='scaffold')
organism_router.register(r'gene', views.NestedGeneViewSet,
                         base_name='gene')
organism_router.register(r'protein', views.NestedProteinViewSet,
                         base_name='protein')

urlpatterns = [
    url(r'^$', views.stats, name='stats'),
    url(r'^stats$', views.stats, name='stats'),
    url(r'api/', include_docs_urls(title='machado API')),
    url(r'api/', include(router.urls)),
    url(r'api/', include(analysis_router.urls)),
    url(r'api/', include(cv_router.urls)),
    url(r'api/', include(db_router.urls)),
    url(r'api/', include(organism_router.urls)),
]
