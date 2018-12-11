# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""transcript views."""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from machado.loaders.common import retrieve_ontology_term
from machado.models import Feature, Featureloc, Featureprop


def get_queryset(request):
    """Summary."""
    current_organism_id = request.session.get('current_organism_id')
    so_term_transcript = retrieve_ontology_term(ontology='sequence',
                                                term='mRNA')
    cv_term_display = retrieve_ontology_term(
        ontology='feature_property', term='display')
    feature_id = request.GET.get('feature_id')

    feature = dict()
    feature['feature_id'] = feature_id
    feature['organism'] = request.session.get('current_organism_name')
    if request.GET.get('feature_id') is not None:
        feature_obj = Feature.objects.get(
            feature_id=feature_id,
            organism_id=current_organism_id,
            type_id=so_term_transcript.cvterm_id)

        feature['name'] = feature_obj.name
        feature['uniquename'] = feature_obj.uniquename

        cv_term_display = retrieve_ontology_term(
            ontology='feature_property', term='display')
        try:
            feature_prop = Featureprop.objects.get(
                type_id=cv_term_display.cvterm_id,
                feature_id=feature_id)
            feature['display'] = feature_prop.value
        except ObjectDoesNotExist:
            pass

        locations = Featureloc.objects.filter(feature_id=feature_id)
        feature['locations'] = list()
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
                                  settings.MACHADO_JBROWSE_URL,
                                  request.session.get('current_organism_name'),
                                  loc)
            feature['locations'].append({
                'start': location.fmin,
                'end': location.fmax,
                'strand': location.strand,
                'ref': Feature.objects.get(
                    feature_id=location.srcfeature_id).uniquename,
                'jbrowse_url': jbrowse_url,
            })

        return render(request,
                      'transcript.html',
                      {'context': feature})
    else:
        feature = [{'error': 'Not found.'}]
