# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""common views."""

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from machado.loaders.common import retrieve_ontology_term
from machado.models import Feature, Featureprop
from typing import Dict, List


def get_queryset(request):
    """Summary."""
    current_organism_id = request.session.get('current_organism_id')
    so_term_transcript = retrieve_ontology_term(ontology='sequence',
                                                term='mRNA')

    if request.GET.get('transcript_id') is not None:
        transcripts = Feature.objects.filter(
            organism_id=current_organism_id,
            type_id=so_term_transcript.cvterm_id,
            uniquename__icontains=request.GET.get('transcript_id'))
        transcripts = transcripts.values_list('feature_id', flat=True)

    if request.GET.get('transcript_keyword') is not None:
        transcripts = Feature.objects.filter(
            organism_id=current_organism_id,
            type_id=so_term_transcript.cvterm_id,
            uniquename__icontains=request.GET.get('transcript_keyword'))
        transcripts = transcripts.values_list('feature_id', flat=True)

    if transcripts is not None:

        transcripts = transcript_details(transcripts)

        # pagination
        paginator = Paginator(transcripts, 20)
        page = request.GET.get('page', 1)

        try:
            transcripts = paginator.page(page)
        except PageNotAnInteger:
            transcripts = paginator.page(1)
        except EmptyPage:
            transcripts = paginator.page(paginator.num_pages)

        # preserve GET parameters
        get_copy = request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()

        return render(request,
                      'summary.html',
                      {'context': transcripts, 'parameters': parameters, })
    else:
        return render(request, 'query')


def transcript_details(transcripts: List[int]) -> List[Dict]:
    """Transcript details."""
    cv_term_display = retrieve_ontology_term(ontology='feature_property',
                                             term='display')

    transcript_details = Feature.objects.filter(feature_id__in=transcripts)
    transcript_details = transcript_details.values(
        'feature_id', 'name', 'uniquename')
    transcript_details = transcript_details.order_by('uniquename')

    for transcript in transcript_details:
        try:
            feature_prop = Featureprop.objects.get(
                type_id=cv_term_display.cvterm_id,
                feature_id=transcript['feature_id'])
            transcript['display'] = feature_prop.value
        except ObjectDoesNotExist:
            pass

    if len(transcript_details) == 0:
        transcript_details = [{'uniquename': 'Not found.'}]

    return transcript_details
