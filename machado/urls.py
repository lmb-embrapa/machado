# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""URLs."""

from machado.views import common, summary
from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', common.index, name='index'),
    url(r'summary/', summary.summary, name='summary'),
    url(r'stats/', common.stats, name='stats'),
    url(r'api/', include('machado.api.urls')),
]
