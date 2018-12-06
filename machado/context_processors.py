# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""context processors."""

from django.core.exceptions import ObjectDoesNotExist
from machado.models import Feature, Organism


def organism_processor(request):
    """List of organisms."""
    try:
        organism_list = Organism.objects.filter(
            organism_id__in=Feature.objects.distinct(
                'organism_id').values_list('organism_id')
        ).exclude(genus='multispecies').values(
            'organism_id', 'genus', 'species')
    except ObjectDoesNotExist:
        organism_list = None

    return {
        'organism_list': organism_list,
    }
