"""URLs."""

from django.urls import path
from chado import views

urlpatterns = [
    path('', views.index),
    path('stats/', views.stats),
]
