# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""feature views."""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from machado.loaders.common import retrieve_ontology_term
from machado.models import Cvterm
from machado.models import Feature, Featureloc, Featureprop
from machado.models import FeatureRelationship
from typing import Dict, List, Optional

VALID_TYPES = ['mRNA', 'polypeptide']


def get_queryset(request):
    """Summary."""
    current_organism_id = request.session.get('current_organism_id')
    feature_id = request.GET.get('feature_id')

    feature = dict()
    feature['feature_id'] = feature_id
    feature['organism'] = request.session.get('current_organism_name')

    try:
        feature_obj = Feature.objects.get(
            feature_id=feature_id,
            organism_id=current_organism_id)
    except ObjectDoesNotExist:
        error = {'error': 'Feature not found.'}
        return render(request,
                      'error.html',
                      {'context': error})

    feature['type'] = Cvterm.objects.get(cvterm_id=feature_obj.type_id).name
    if feature['type'] not in VALID_TYPES:
        error = {'error': 'Invalid feature type.'}
        return render(request,
                      'error.html',
                      {'context': error})

    transcript = dict()
    protein = dict()
    if feature['type'] == 'mRNA':
        transcript = retrieve_feature_data(request=request,
                                           feature_obj=feature_obj)
        try:
            cvterm_translation_of = retrieve_ontology_term(
                ontology='sequence', term='translation_of')
            protein_id = FeatureRelationship.objects.get(
                subject_id=feature_obj.feature_id,
                type_id=cvterm_translation_of.cvterm_id).object_id
            protein_obj = Feature.objects.get(feature_id=protein_id)
            protein = retrieve_feature_data(request=request,
                                            feature_obj=protein_obj)
        except ObjectDoesNotExist:
            pass

    if feature['type'] == 'polypeptide':
        protein = retrieve_feature_data(request=request,
                                        feature_obj=feature_obj)
    return render(request,
                  'feature.html',
                  {'feature': feature,
                   'transcript': transcript,
                   'protein': protein})


def retrieve_feature_data(request, feature_obj: Feature) -> Dict:
    """Retrieve transcript data."""
    transcript = {
        'feature_id': feature_obj.feature_id,
        'name': feature_obj.name,
        'uniquename': feature_obj.uniquename,
    }

    transcript['display'] = retrieve_feature_prop(
        feature_id=feature_obj.feature_id, prop='display')

    transcript['locations'] = retrieve_feature_locations(
        feature_id=feature_obj.feature_id,
        organism=request.session.get('current_organism_name'))

    return transcript


def retrieve_feature_prop(feature_id: int, prop: str) -> Optional[str]:
    """Retrieve feature general info."""
    cvterm = retrieve_ontology_term(
        ontology='feature_property', term=prop)
    try:
        cvterm = retrieve_ontology_term(
            ontology='feature_property', term=prop)
        feature_prop = Featureprop.objects.get(
            type_id=cvterm.cvterm_id,
            feature_id=feature_id)
        return feature_prop.value
    except ObjectDoesNotExist:
        return None


def retrieve_feature_locations(feature_id: int, organism: str) -> List[Dict]:
    """Retrieve feature locations."""
    locations = Featureloc.objects.filter(feature_id=feature_id)
    result = list()
    for location in locations:
        jbrowse_url = None
        if hasattr(settings, 'MACHADO_JBROWSE_URL'):
            if hasattr(settings, 'MACHADO_JBROWSE_OFFSET'):
                offset = settings.MACHADO_JBROWSE_OFFSET
            else:
                offset = 1000
            loc = '{}:{}..{}'.format(
                Feature.objects.get(
                    feature_id=location.srcfeature_id).uniquename,
                location.fmin - offset,
                location.fmax + offset,
            )
            jbrowse_url = '{}/?data=data/{}&loc={}'\
                          '&tracklist=0&nav=0&overview=0'.format(
                              settings.MACHADO_JBROWSE_URL, organism, loc)
        result.append({
            'start': location.fmin,
            'end': location.fmax,
            'strand': location.strand,
            'ref': Feature.objects.get(
                feature_id=location.srcfeature_id).uniquename,
            'jbrowse_url': jbrowse_url,
        })

    return result
