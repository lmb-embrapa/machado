# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""transcript views."""

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from machado.loaders.common import retrieve_ontology_term
from machado.models import Feature, Featureprop


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

        return render(request,
                      'transcript.html',
                      {'context': feature})
    else:
        feature = [{'error': 'Not found.'}]
