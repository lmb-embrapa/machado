# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Template tags."""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """Return the encoded URL parameters. Replace if the parameter exists."""
    params = context['request'].GET.copy()

    for k, v in kwargs.items():
        if k == 'selected_facets':
            params.appendlist(k, v)
        else:
            params[k] = v

    return params.urlencode()
