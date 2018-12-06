# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""index views."""

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Organism


def index(request):
    """Index."""
    if request.GET.get('current_organism_id') is not None:
        try:
            organism_obj = Organism.objects.get(
                organism_id=request.GET.get('current_organism_id'))
            request.session['current_organism_id'] = request.GET.get(
                'current_organism_id')
            request.session['current_organism_name'] = '{} {}'.format(
                organism_obj.genus, organism_obj.species)
        except (ObjectDoesNotExist, ValueError):
            request.session['current_organism_id'] = None
            request.session['current_organism_name'] = None

    if 'current_organism_id' not in request.session:
        request.session['current_organism_id'] = None
        request.session['current_organism_name'] = None

    data = 'Hello, world.'
    return render(request, 'index.html', {'context': data})
