"""URLs."""

from chado import views
from django.conf.urls import include, url
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r'organism', views.OrganismViewSet, base_name='organism')
router.register(r'cv', views.CvViewSet, base_name='cv')
router.register(r'cvterm', views.CvtermViewSet, base_name='cvterm')

cv_router = routers.NestedSimpleRouter(router, r'cv', lookup='cv')
cv_router.register(r'cvterm', views.NestedCvtermViewSet)

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stats$', views.stats, name='stats'),
    url(r'api/', include(router.urls)),
    url(r'api/', include(cv_router.urls))
]
