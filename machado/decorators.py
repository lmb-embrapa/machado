# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Decorators."""
from django.core.exceptions import ObjectDoesNotExist


def get_display(self):
    """Get the display feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name='display',
            type__cv__name='feature_property').value
    except ObjectDoesNotExist:
        return None


def get_description(self):
    """Get the description feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name='description',
            type__cv__name='feature_property').value
    except ObjectDoesNotExist:
        return None


def get_note(self):
    """Get the note feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name='note',
            type__cv__name='feature_property').value
    except ObjectDoesNotExist:
        return None


def get_orthologs_groups(self):
    """Get the orthologous group id."""
    result = list()
    feature_relationships = self.FeatureRelationship_subject_Feature.filter(
        type__name='in orthology relationship with',
        type__cv__name='relationship').distinct("value")
    for feature_relationship in feature_relationships:
        result.append(feature_relationship.value)
    return result


def machadoFeatureMethods():
    """Add methods to machado.models.Feature."""
    def wrapper(cls):
        setattr(cls, 'get_display', get_display)
        setattr(cls, 'get_description', get_description)
        setattr(cls, 'get_note', get_note)
        setattr(cls, 'get_orthologs_groups', get_orthologs_groups)
        return cls
    return wrapper
