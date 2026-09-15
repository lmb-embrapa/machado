# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Template tags."""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """Return the encoded URL parameters. Replace if the parameter exists."""
    params = context["request"].GET.copy()

    for k, v in kwargs.items():
        if k == "selected_facets":
            params.appendlist(k, v)
        elif k == "order_by":
            if k in params and params[k] == v:
                params[k] = "-{}".format(v)
            else:
                params[k] = v
        else:
            params[k] = v

    return params.urlencode()


@register.simple_tag(takes_context=True)
def remove_query(context, *args):
    """Return the encoded URL parameters. Remove query."""
    params = context["request"].GET.copy()
    params.setlist("q", "")
    return params.urlencode()


@register.simple_tag(takes_context=True)
def remove_facet(context, *args):
    """Return the encoded URL parameters. Remove facet."""
    params = context["request"].GET.copy()

    for facet in args:
        params_new = list()
        for i in params.getlist("selected_facets"):
            k, v = i.split(":")
            if not k.startswith(facet):
                params_new.append(i)
        params.setlist("selected_facets", params_new)

    return params.urlencode()


@register.simple_tag(takes_context=True)
def remove_facet_field(context, *args):
    """Return the encoded URL parameters. Remove facet field."""
    params = context["request"].GET.copy()

    for facet_field in args:
        params_new = list()
        for i in params.getlist("selected_facets"):
            if not i.startswith(facet_field):
                params_new.append(i)
        params.setlist("selected_facets", params_new)

    return params.urlencode()


@register.filter
def get_item(self, key):
    """Return the dictionary value."""
    return self.get(key)


@register.filter
def get_count(self, key):
    """Return the dictionary value."""
    return len(self.get(key))


@register.filter
def split(value, arg):
    """Split."""
    return value.split(arg)


@register.filter
def richtext(value):
    r"""Render an administrator-authored text that may carry links and breaks.

    Used for the landing page's How It Works body and Acknowledgements, whose
    values come from .env and are therefore written by whoever deploys the
    instance -- never by a site visitor. That is why the markup is emitted
    unescaped: there is no untrusted input path into these settings, and
    escaping them would defeat their whole purpose, which is to let a
    deployment link out to a funder or a documentation page.

    A dotenv value is always a single line, so a line break has to be written
    as the two characters backslash-n; both that and a real newline become a
    <br>.
    """
    if not value:
        return ""
    return mark_safe(str(value).replace("\\n", "\n").replace("\n", "<br>"))
