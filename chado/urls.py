"""URLs."""

from chado import views
from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'organism', views.OrganismViewSet)

urlpatterns = [
    path('', views.index),
    path('stats/', views.stats),
    url(r'api/', include(router.urls)),
]
