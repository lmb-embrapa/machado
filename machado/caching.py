# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Whole-page caching for the read-heavy search views.

The corpus is loaded once and then only read, so a rendered page stays
correct until the search index is rebuilt -- which is the only event that
invalidates anything (see the ``cache.clear()`` calls in
``rebuild_search_index``). Entries therefore never expire on their own.
"""

import functools
import hashlib

from django.core.cache import cache
from django.http import HttpResponse

#: Bumped only if the stored representation changes shape, so an old cache
#: cannot be misread as a new one.
_CACHE_VERSION = "v1"


def _is_authenticated(request):
    """Whether the request comes from a logged-in user."""
    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated)


def page_cache_key(request, authenticated):
    """Build the cache key for one rendered page.

    Query parameters are sorted, and their values sorted within each
    parameter, so requests that mean the same thing share one entry:
    ``selected_facets`` arrives in whatever order the user happened to tick
    the boxes, and ``?a=1&b=2`` is the same page as ``?b=2&a=1``. Django's
    own ``cache_page`` keys on the raw URL and would store those separately.

    ``authenticated`` is part of the key because anonymous and logged-in
    users see different result sets -- an anonymous visitor has private
    organisms filtered out (see ``_excluded_organism_names``). Nothing
    finer is needed: visibility turns on ``is_authenticated`` alone, never
    on which user, so all logged-in users share one entry.

    Deliberately NOT keyed on cookies, even though these responses carry
    ``Vary: Cookie``. Honouring that -- as ``cache_page`` would -- gives
    every distinct cookie value its own entry, so each anonymous visitor
    holding a ``csrftoken`` would miss and store a near-duplicate page.
    The two buckets above are the only ones that differ in content.
    """
    params = sorted(
        (name, sorted(request.GET.getlist(name))) for name in request.GET.keys()
    )
    raw = repr((_CACHE_VERSION, request.path, params, authenticated))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return "machado.page.{}.{}".format(
        "auth" if authenticated else "anon",
        digest,
    )


def cache_page_per_auth(view):
    """Cache a view's rendered output, separately for the two audiences.

    Only GET requests, and only successful responses, are stored. A
    ``TemplateResponse`` is not rendered when the view returns it, so
    storing is deferred to a post-render callback -- otherwise ``.content``
    raises and nothing would ever be cached.
    """

    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method != "GET":
            return view(request, *args, **kwargs)

        authenticated = _is_authenticated(request)
        key = page_cache_key(request, authenticated)

        hit = cache.get(key)
        if hit is not None:
            return HttpResponse(
                hit["content"],
                content_type=hit["content_type"],
            )

        response = view(request, *args, **kwargs)

        def store(rendered):
            if rendered.status_code == 200:
                cache.set(
                    key,
                    {
                        "content": rendered.content,
                        "content_type": rendered.get("Content-Type"),
                    },
                    timeout=None,
                )
            return rendered

        if hasattr(response, "add_post_render_callback"):
            response.add_post_render_callback(store)
        else:
            store(response)
        return response

    return wrapper
