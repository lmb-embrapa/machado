# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""common views."""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        if genes is None:
            genes = 'result not found'

    if genes is not None:

        genes = gene_details(genes)

        # pagination
        paginator = Paginator(genes, 20)
        page = request.GET.get('page', 1)

        try:
            genes = paginator.page(page)
        except PageNotAnInteger:
            genes = paginator.page(1)
        except EmptyPage:
            genes = paginator.page(paginator.num_pages)

        # preserve GET parameters
        get_copy = request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()

        return render(request,
                      'summary.html',
                      {'context': genes, 'parameters': parameters, })
    else:
        return render(request, 'query')


def gene_details(genes: List[int]) -> List[Dict]:
    """Gene details."""
    details = Feature.objects.filter(feature_id__in=genes)
    details = details.values('name', 'uniquename')
    details = details.order_by('uniquename')

    if len(details) == 0:
        details = [{'uniquename': 'Not found.'}]

    return details
