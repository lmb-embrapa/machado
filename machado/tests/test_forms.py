"""Module tests."""

from django.test import TestCase
from django.http import QueryDict
from unittest.mock import MagicMock, patch

from machado.forms import FeatureSearchForm
from django.contrib.postgres.search import SearchQuery


class FeatureSearchFormTest(TestCase):
    """Test suite for FeatureSearchForm."""

    def test_search_invalid(self):
        """Test search invalid."""
        form = FeatureSearchForm(data={})
        # Mock is_valid since we are just testing search logic
        form.is_valid = MagicMock(return_value=False)
        form.cleaned_data = {}

        # The real form returns FeatureSearchIndex.objects.none() if invalid,
        # but the view does the is_valid check.
        # If we just call search directly with an empty/invalid form, it applies an empty 'q'
        with patch("machado.forms.FeatureSearchIndex.objects.all") as mock_all:
            mock_qs = MagicMock()
            mock_all.return_value = mock_qs
            result = form.search()
            self.assertEqual(result, mock_qs)

    def test_search_empty_q(self):
        """Test search empty q."""
        data = QueryDict(mutable=True)
        data.update({"q": ""})

        form = FeatureSearchForm(data=data)
        form.is_valid = MagicMock(return_value=True)
        form.cleaned_data = {"q": ""}

        with patch("machado.forms.FeatureSearchIndex.objects.all") as mock_all:
            mock_qs = MagicMock()
            mock_all.return_value = mock_qs

            result = form.search()
            self.assertEqual(result, mock_qs)

    def test_search_with_q(self):
        """Test search with q."""
        data = QueryDict(mutable=True)
        data.update({"q": "test"})

        form = FeatureSearchForm(data=data)
        form.is_valid = MagicMock(return_value=True)
        form.cleaned_data = {"q": "test"}

        with patch("machado.forms.FeatureSearchIndex.objects.all") as mock_all:
            mock_qs = MagicMock()
            mock_all.return_value = mock_qs
            mock_annotated = MagicMock()
            mock_annotated.exists.return_value = True
            mock_qs.filter.return_value.annotate.return_value = mock_annotated

            result = form.search()
            self.assertEqual(result, mock_annotated)

            # verify it filters by search_vector
            filter_kwargs = mock_qs.filter.call_args[1]
            self.assertIn("search_vector", filter_kwargs)
            self.assertIsInstance(filter_kwargs["search_vector"], SearchQuery)

    def test_search_with_facets(self):
        """Test search with facets."""
        data = QueryDict(mutable=True)
        data.update({"q": "test"})
        # selected_facets is passed via method arg in new design, not via POST data
        selected_facets = ["analyses:A", "analyses:B", "so_term:C", "so_term:D"]

        form = FeatureSearchForm(data=data)
        form.is_valid = MagicMock(return_value=True)
        form.cleaned_data = {"q": "test"}

        with patch("machado.forms.FeatureSearchIndex.objects.all") as mock_all:
            mock_qs = MagicMock()
            mock_all.return_value = mock_qs

            # Mocks for facet chaining
            mock_qs.filter.return_value = mock_qs
            mock_annotated = MagicMock()
            mock_annotated.exists.return_value = True
            mock_qs.annotate.return_value = mock_annotated

            result = form.search(selected_facets=selected_facets)
            self.assertEqual(result, mock_annotated)

            # sqs.filter should have been called multiple times
            self.assertTrue(mock_qs.filter.called)

    def test_search_with_wildcard(self):
        """Test wildcard search with '*'."""
        data = QueryDict(mutable=True)
        data.update({"q": "test*"})
        form = FeatureSearchForm(data=data)
        form.is_valid = MagicMock(return_value=True)
        form.cleaned_data = {"q": "test*"}

        with patch("machado.forms.FeatureSearchIndex.objects.all") as mock_all:
            mock_qs = MagicMock()
            mock_all.return_value = mock_qs
            # Mock .exists() to avoid fallback during this test
            mock_qs.filter.return_value.annotate.return_value.exists.return_value = True

            form.search()

            # Verify SearchQuery uses raw search (to_tsquery) and contains ':*'
            query = mock_qs.filter.call_args[1]["search_vector"]
            # Django's SearchQuery stores the function ('to_tsquery' for raw)
            self.assertEqual(query.function, "to_tsquery")
            # The query value is usually the second source expression
            self.assertIn("test:*", str(query.source_expressions[1]))

    def test_apply_facets_normalizes_boolean_values(self):
        """Boolean-like facet values (any case) must become Python bool for __in lookups."""
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs

        FeatureSearchForm._apply_facets(
            mock_qs,
            ["orthology:false", "orthology:True"],
        )

        filter_kwargs = mock_qs.filter.call_args[1]
        self.assertEqual(filter_kwargs["orthology__in"], [False, True])

    def test_search_substring_fallback(self):
        """Test fallback to icontains if FTS yields no results."""
        data = QueryDict(mutable=True)
        data.update({"q": "ATMG"})
        form = FeatureSearchForm(data=data)
        form.is_valid = MagicMock(return_value=True)
        form.cleaned_data = {"q": "ATMG"}

        with patch("machado.forms.FeatureSearchIndex.objects.all") as mock_all:
            mock_qs = MagicMock()
            mock_all.return_value = mock_qs

            # Mock FTS results and fallback results
            fts_results = MagicMock()
            fts_results.exists.return_value = False  # Trigger fallback

            substring_results = MagicMock()
            substring_results.exists.return_value = True

            # mock_qs.filter.return_value is what .annotate is called on
            annotatable_qs = mock_qs.filter.return_value
            annotatable_qs.annotate.side_effect = [fts_results, substring_results]

            form.search()

            # The second filter call should be the fallback substring search
            self.assertEqual(mock_qs.filter.call_count, 2)

            # Verify that annotate was called twice on the filtered queryset
            self.assertEqual(annotatable_qs.annotate.call_count, 2)

            # Check the second call to annotate (the fallback one)
            fallback_annotate_args = annotatable_qs.annotate.call_args_list[1]
            rank_arg = fallback_annotate_args[1]["rank"]
            from django.db.models import Value

            self.assertIsInstance(rank_arg, Value)
            self.assertEqual(rank_arg.value, 0.0)

            # Verify the fallback filter had Q objects or icontains
            fallback_filter_args = mock_qs.filter.call_args_list[1]
            self.assertTrue(
                any("icontains" in str(arg) for arg in fallback_filter_args[0])
            )
