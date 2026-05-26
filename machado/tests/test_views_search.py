"""Tests for search views."""

from django.test import TestCase, RequestFactory
from machado.views.search import FeatureSearchView, FeatureSearchExportView
from unittest.mock import patch, MagicMock


class SearchViewsTest(TestCase):
    """Test suite for search-related views."""

    def setUp(self):
        """Set up the test case with a request factory."""
        self.factory = RequestFactory()

    @patch("machado.views.search.FeatureSearchForm")
    def test_feature_search_view_get_queryset(self, mock_form_class):
        """Test get_queryset of FeatureSearchView with pagination and ordering."""
        mock_form = MagicMock()
        mock_form_class.return_value = mock_form
        mock_form.is_valid.return_value = True

        mock_qs = MagicMock()
        mock_form.search.return_value = mock_qs
        mock_qs.exclude.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs

        request = self.factory.get("/find/?q=test&order_by=name&records=10")
        view = FeatureSearchView()
        view.request = request
        view.kwargs = {}

        qs = view.get_queryset()

        # Verify pagination and order_by
        self.assertEqual(view.paginate_by, 10)
        mock_qs.order_by.assert_called_with("name")
        self.assertEqual(qs, mock_qs)

    @patch("machado.views.search.FeatureSearchForm")
    def test_feature_search_view_get_queryset_defaults(self, mock_form_class):
        """Test get_queryset of FeatureSearchView with default values."""
        mock_form = MagicMock()
        mock_form_class.return_value = mock_form
        mock_form.is_valid.return_value = True

        mock_qs = MagicMock()
        mock_form.search.return_value = mock_qs
        mock_qs.exclude.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs

        request = self.factory.get("/find/")
        view = FeatureSearchView()
        view.request = request
        view.kwargs = {}

        view.get_queryset()

        self.assertEqual(view.paginate_by, 50)
        mock_qs.order_by.assert_called_with("uniquename")

    @patch("machado.views.search.ListView.get_context_data")
    def test_feature_search_view_get_context_data(self, mock_super_get_context):
        """Test context data preparation in FeatureSearchView."""
        mock_super_get_context.return_value = {}

        request = self.factory.get(
            "/find/?selected_facets=so_term:gene&selected_facets=other:val"
        )
        view = FeatureSearchView()
        view.request = request
        view.kwargs = {}

        # Mock the queryset used for facets
        mock_qs = MagicMock()
        # Create a mock query result that yields the correct format for any field requested
        mock_qs.values.return_value.annotate.return_value.filter.return_value.order_by.side_effect = lambda f: [
            {f: "val", "count": 1}
        ]
        view._queryset_for_facets = mock_qs

        # Mock array facet computation
        with patch.object(view, "_compute_array_facet", return_value=[("blast", 1)]):
            with patch("machado.views.search.Featureprop.objects.filter") as mock_fp:
                mock_fp.return_value.exists.return_value = False
                context = view.get_context_data()

        self.assertEqual(context["so_term_count"], 1)
        self.assertIn("so_term", context["selected_facets_fields"])
        self.assertIn("other", context["selected_facets_fields"])
        self.assertEqual(context["facets"]["fields"]["so_term"], [("val", 1)])

    @patch("machado.views.search.ListView.get_context_data")
    def test_feature_search_export_view_get_context_data(self, mock_super_get_context):
        """Test context data preparation in FeatureSearchExportView."""
        mock_super_get_context.return_value = {}

        request = self.factory.get("/export/?export=fasta")
        view = FeatureSearchExportView()
        view.request = request
        view.kwargs = {}

        context = view.get_context_data()
        self.assertEqual(context["file_format"], "fasta")
        self.assertEqual(view.file_format, "fasta")

    @patch("machado.views.search.ListView.get_context_data")
    def test_feature_search_export_view_get_context_data_default(
        self, mock_super_get_context
    ):
        """Test default context data in FeatureSearchExportView."""
        mock_super_get_context.return_value = {}

        request = self.factory.get("/export/")
        view = FeatureSearchExportView()
        view.request = request
        view.kwargs = {}
        view.object_list = []

        context = view.get_context_data()
        self.assertEqual(context["file_format"], "tsv")

    @patch("machado.views.search.ListView.dispatch")
    def test_feature_search_export_view_dispatch(self, mock_super_dispatch):
        """Test dispatch method of FeatureSearchExportView."""
        mock_response = {}
        mock_super_dispatch.return_value = mock_response

        view = FeatureSearchExportView()
        view.file_format = "fasta"
        view.kwargs = {}
        view.object_list = []

        request = self.factory.get("/export/?export=fasta")
        # Ensure file_format is populated
        view.request = request
        view.get_context_data()

        response = view.dispatch(request)

        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="machado_search_results.fasta"',
        )
