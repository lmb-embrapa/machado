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


def machadoFeatureMethods():
    """Add methods to machado.models.Feature."""
    def wrapper(cls):
        setattr(cls, 'get_display', get_display)
        return cls
    return wrapper
