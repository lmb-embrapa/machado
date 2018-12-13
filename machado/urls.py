# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from machado.views import common, summary, feature
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', common.index, name='index'),
    url(r'summary/', summary.get_queryset, name='summary'),
    url(r'feature/', feature.get_queryset, name='feature'),
    url(r'data-numbers/', common.data_numbers, name='data-numbers'),
    url(r'api/', include('machado.api.urls')),
]
