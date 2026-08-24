"""Tests for search views."""

from django.test import TestCase, RequestFactory
from machado.models import (
    Cv,
    Cvterm,
    Db,
    Dbxref,
    Feature,
    FeatureSearchIndex,
    Organism,
    Organismprop,
)
from machado.views.search import (
    FeatureSearchView,
    FeatureSearchExportView,
    _excluded_organism_names,
)
from unittest.mock import patch, MagicMock


class ComputeArrayFacetTest(TestCase):
    """_compute_array_facet must count every matching row, not a fixed sample."""

    def setUp(self):
        """Create features whose 'analyses' facet values outnumber any small cap."""
        db = Db.objects.create(name="local")
        dbxref = Dbxref.objects.create(db=db, accession="gene")
        cv = Cv.objects.create(name="sequence")
        cvterm = Cvterm.objects.create(
            cv=cv, name="gene", dbxref=dbxref, is_obsolete=0, is_relationshiptype=0
        )
        org = Organism.objects.create(genus="Gen", species="spec")

        # 7 rows tagged "blast", 3 tagged "interpro" -- an old fixed-size
        # sample (e.g. the first N rows) could easily miss or truncate one
        # of these groups; the count returned must match .filter().count()
        # for every value, not just be non-empty.
        for i in range(7):
            feature = Feature.objects.create(
                organism=org,
                uniquename=f"blast_feature_{i}",
                type=cvterm,
                is_analysis=False,
                is_obsolete=False,
                timeaccessioned="2023-01-01T00:00:00Z",
                timelastmodified="2023-01-01T00:00:00Z",
            )
            FeatureSearchIndex.objects.create(feature=feature, analyses=["blast"])
        for i in range(3):
            feature = Feature.objects.create(
                organism=org,
                uniquename=f"interpro_feature_{i}",
                type=cvterm,
                is_analysis=False,
                is_obsolete=False,
                timeaccessioned="2023-01-01T00:00:00Z",
                timelastmodified="2023-01-01T00:00:00Z",
            )
            FeatureSearchIndex.objects.create(feature=feature, analyses=["interpro"])

    def test_counts_every_matching_row(self):
        """Facet counts must equal the real filtered count for each value."""
        qs = FeatureSearchIndex.objects.all()
        facet = dict(FeatureSearchView._compute_array_facet(qs, "analyses"))

        self.assertEqual(facet["blast"], 7)
        self.assertEqual(facet["interpro"], 3)
        self.assertEqual(
            facet["blast"], qs.filter(analyses__contains=["blast"]).count()
        )
        self.assertEqual(
            facet["interpro"], qs.filter(analyses__contains=["interpro"]).count()
        )


class ExcludedOrganismNamesTest(TestCase):
    """Test suite for _excluded_organism_names."""

    def setUp(self):
        """Create a public and a private organism.

        The multispecies pseudo-organism is already seeded by migration
        0003_add_multispecies, so it isn't created here.
        """
        db = Db.objects.create(name="local")
        dbxref = Dbxref.objects.create(db=db, accession="is_public")
        cv = Cv.objects.create(name="organism_property")
        cvterm = Cvterm.objects.create(
            cv=cv,
            name="is_public",
            is_obsolete=0,
            is_relationshiptype=0,
            dbxref=dbxref,
        )

        self.public_org = Organism.objects.create(genus="Arabidopsis", species="thaliana")
        self.private_org = Organism.objects.create(genus="Oryza", species="sativa")
        Organismprop.objects.create(
            organism=self.private_org, type=cvterm, value="false", rank=0
        )

    def test_anonymous_excludes_multispecies_and_private(self):
        """Anonymous users must not see the multispecies or private organisms."""
        names = _excluded_organism_names(anonymous=True)
        self.assertIn("multispecies multispecies", names)
        self.assertIn("Oryza sativa", names)
        self.assertNotIn("Arabidopsis thaliana", names)

    def test_authenticated_excludes_only_multispecies(self):
        """Authenticated users may see private organisms, never multispecies."""
        names = _excluded_organism_names(anonymous=False)
        self.assertIn("multispecies multispecies", names)
        self.assertNotIn("Oryza sativa", names)
        self.assertNotIn("Arabidopsis thaliana", names)


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
