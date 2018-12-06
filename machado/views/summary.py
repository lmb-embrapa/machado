# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""common views."""

from django.shortcuts import render
from machado.loaders.common import retrieve_ontology_term
from machado.models import Feature
from typing import Dict, List


def summary(request):
    """Summary."""
    current_organism_id = request.session.get('current_organism_id')
    so_term_gene = retrieve_ontology_term(ontology='sequence',
                                          term='gene')

    if request.GET.get('gene_id') is not '':
        genes = Feature.objects.filter(
            organism_id=current_organism_id,
            type_id=so_term_gene.cvterm_id,
            uniquename__contains=request.GET.get('gene_id'))
        genes = genes.values_list('feature_id', flat=True)
        return render(request,
                      'summary.html',
                      {'context': gene_details(genes)})
    else:
        return render(request, 'query')


def gene_details(genes: List[int]) -> List[Dict]:
    """Gene details."""
    details = Feature.objects.filter(feature_id__in=genes)
    details = details.values('name', 'uniquename')
    return details
