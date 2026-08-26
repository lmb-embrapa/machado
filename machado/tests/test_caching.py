# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for whole-page caching of the search views."""

import tempfile

from django.contrib.auth.models import AnonymousUser, User
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from machado.caching import cache_page_per_auth, page_cache_key

FILE_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": tempfile.mkdtemp(prefix="machado-test-cache-"),
        "TIMEOUT": None,
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }
}


@override_settings(CACHES=FILE_CACHE)
class PageCacheKeyTest(TestCase):
    """What the key does and does not distinguish."""

    def setUp(self):
        """Start from an empty cache."""
        cache.clear()
        self.factory = RequestFactory()

    def _key(self, query, authenticated=False):
        return page_cache_key(self.factory.get("/find/", query), authenticated)

    def test_anonymous_and_authenticated_never_share_an_entry(self):
        """The two audiences see different results, so they must not collide.

        An anonymous visitor has private organisms filtered out. Sharing a
        cache entry would serve them a page built for a logged-in user.
        """
        self.assertNotEqual(self._key({}, False), self._key({}, True))

    def test_facet_order_does_not_split_the_entry(self):
        """Ticking the same boxes in a different order is the same page."""
        a = self._key({"selected_facets": ["organism:Zea mays", "so_term:gene"]})
        b = self._key({"selected_facets": ["so_term:gene", "organism:Zea mays"]})
        self.assertEqual(a, b)

    def test_parameter_order_does_not_split_the_entry(self):
        """?a=1&b=2 is the same page as ?b=2&a=1."""
        self.assertEqual(
            page_cache_key(self.factory.get("/find/?q=kinase&order_by=name"), False),
            page_cache_key(self.factory.get("/find/?order_by=name&q=kinase"), False),
        )

    def test_different_queries_do_not_share_an_entry(self):
        """Distinct searches are distinct pages."""
        self.assertNotEqual(self._key({"q": "kinase"}), self._key({"q": "kinesin"}))

    def test_different_facet_selections_do_not_share_an_entry(self):
        """Selecting an extra facet is a different page."""
        self.assertNotEqual(
            self._key({"selected_facets": ["so_term:gene"]}),
            self._key({"selected_facets": ["so_term:gene", "organism:Zea mays"]}),
        )


@override_settings(CACHES=FILE_CACHE)
class CachePagePerAuthTest(TestCase):
    """The decorator's behaviour around who gets served what."""

    def setUp(self):
        """Start from an empty cache with a counting view."""
        cache.clear()
        self.factory = RequestFactory()
        self.calls = []

        @cache_page_per_auth
        def view(request):
            self.calls.append(request)
            who = "auth" if request.user.is_authenticated else "anon"
            return HttpResponse(f"page for {who} #{len(self.calls)}")

        self.view = view

    def _get(self, user, **query):
        request = self.factory.get("/find/", query)
        request.user = user
        return self.view(request)

    def test_second_identical_request_is_served_from_cache(self):
        """A repeat request must not reach the view again."""
        first = self._get(AnonymousUser())
        second = self._get(AnonymousUser())
        self.assertEqual(first.content, second.content)
        self.assertEqual(len(self.calls), 1, "the view ran twice")

    def test_authenticated_user_does_not_receive_the_anonymous_page(self):
        """The cached anonymous page must not leak to a logged-in user."""
        anon_body = self._get(AnonymousUser()).content
        user = User.objects.create_user(username="someone", password="pw")
        auth_body = self._get(user).content

        self.assertNotEqual(anon_body, auth_body)
        self.assertIn(b"for auth", auth_body)
        self.assertEqual(len(self.calls), 2, "the view should have run for each")

    def test_anonymous_user_does_not_receive_the_authenticated_page(self):
        """And the reverse: a logged-in page must not leak to anonymous."""
        user = User.objects.create_user(username="someone", password="pw")
        auth_body = self._get(user).content
        anon_body = self._get(AnonymousUser()).content

        self.assertNotEqual(auth_body, anon_body)
        self.assertIn(b"for anon", anon_body)

    def test_all_authenticated_users_share_one_entry(self):
        """Visibility turns on is_authenticated, never on which user.

        Keying per user would multiply the cache by the number of accounts
        for no difference in content.
        """
        one = User.objects.create_user(username="one", password="pw")
        two = User.objects.create_user(username="two", password="pw")
        self.assertEqual(self._get(one).content, self._get(two).content)
        self.assertEqual(len(self.calls), 1)

    def test_post_is_not_cached(self):
        """Only GET is cached."""
        request = self.factory.post("/find/")
        request.user = AnonymousUser()
        self.view(request)
        self.view(request)
        self.assertEqual(len(self.calls), 2)

    def test_error_responses_are_not_cached(self):
        """A failure must not be served to everyone until the next rebuild."""
        calls = []

        @cache_page_per_auth
        def failing(request):
            calls.append(request)
            return HttpResponse("boom", status=500)

        request = self.factory.get("/find/")
        request.user = AnonymousUser()
        failing(request)
        failing(request)
        self.assertEqual(len(calls), 2, "a 500 was cached")

    def test_clearing_the_cache_makes_the_view_run_again(self):
        """This is what rebuild_search_index relies on for invalidation."""
        self._get(AnonymousUser())
        cache.clear()
        self._get(AnonymousUser())
        self.assertEqual(len(self.calls), 2)
