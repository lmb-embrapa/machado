# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
"""Whole-page caching for the read-heavy search and summary views.

The corpus is loaded once and then only read, so a rendered page stays
correct until something changes what it would render. Two events do:
rebuilding the search index, and changing an organism's visibility (which
moves rows in and out of what an anonymous visitor may see). Both route
through :func:`clear_page_cache`. Entries never expire on their own, so an
event that does not route through there leaves pages stale indefinitely.
"""

import functools
import hashlib
import logging
import os
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.checks import Warning as CheckWarning
from django.http import HttpResponse

logger = logging.getLogger(__name__)

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


def _read(key):
    """Read a cached page, treating any backend failure as a miss.

    Deliberately catching everything a backend might raise. The cache is an
    optimisation, and a page that cannot be cached should be slow rather
    than unavailable -- but FileBasedCache raises PermissionError from its
    own constructor when it cannot create its directory, so without this an
    unwritable CACHE_DIR turns every search into a 500. The failure is
    logged on every request rather than silently swallowed, and
    check_cache_directory() reports the same condition at deploy time.
    """
    try:
        return cache.get(key)
    except Exception:
        logger.warning("page cache unreadable; serving uncached", exc_info=True)
        return None


def _write(key, value):
    """Store a rendered page, ignoring a backend that cannot accept it."""
    try:
        cache.set(key, value, timeout=None)
    except Exception:
        logger.warning("page cache unwritable; not caching", exc_info=True)


def clear_page_cache():
    """Drop every cached page, treating a broken backend as nothing to do.

    Called whenever something changes what a cached page would render:
    rebuilding the search index, and changing an organism's visibility. The
    cache holds no expiry of its own, so an event that is not routed through
    here leaves the affected pages stale indefinitely.

    Deliberately clearing everything rather than the affected keys. A page's
    key is a digest of its query parameters, so the entries touched by one
    organism turning private cannot be enumerated -- and the pages that must
    go are exactly the ones whose facet counts mention it, which is most of
    them. Rebuilding a handful of pages costs less than being wrong.

    Failures are swallowed for the same reason as in _read and _write: an
    unusable cache must make the site slower, never broken.
    """
    try:
        cache.clear()
    except Exception:
        logger.warning("page cache could not be cleared", exc_info=True)


def check_cache_directory(app_configs, **kwargs):
    """Warn when a FileBasedCache directory is not usable.

    Registered as a system check so it runs on ``manage.py check`` -- and
    therefore on ``runserver`` and before most management commands -- which
    is where an operator setting the project up will see it. A warning
    rather than an error: the site works without its page cache, only
    slower, so this must never block a deploy.
    """
    config = (getattr(settings, "CACHES", None) or {}).get("default") or {}
    if not config.get("BACKEND", "").endswith("filebased.FileBasedCache"):
        return []

    location = config.get("LOCATION")
    if not location:
        return []

    try:
        os.makedirs(location, mode=0o700, exist_ok=True)
        # Creating the directory is not enough: it can exist while being
        # owned by another user, which is the usual production mistake
        # (Apache made it, or the operator did). Only a write proves it.
        with tempfile.NamedTemporaryFile(dir=location):
            pass
    except OSError as error:
        return [
            CheckWarning(
                "The page cache directory is not writable: {}".format(error),
                hint=(
                    "Search pages will be rebuilt on every request until this "
                    "is fixed. Point CACHE_DIR at a directory writable by "
                    "both the web server and whoever runs "
                    "rebuild_search_index."
                ),
                id="machado.W001",
            )
        ]
    return []


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

        hit = _read(key)
        if hit is not None:
            return HttpResponse(
                hit["content"],
                content_type=hit["content_type"],
            )

        response = view(request, *args, **kwargs)

        def store(rendered):
            if rendered.status_code == 200:
                _write(
                    key,
                    {
                        "content": rendered.content,
                        "content_type": rendered.get("Content-Type"),
                    },
                )
            return rendered

        if hasattr(response, "add_post_render_callback"):
            response.add_post_render_callback(store)
        else:
            store(response)
        return response

    return wrapper
