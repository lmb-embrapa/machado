"""Tests for search views."""

from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.test import TestCase, RequestFactory, override_settings
from machado.models import (
    Cv,
    Cvterm,
    Db,
    Dbxref,
    Feature,
    FeatureSearchIndex,
    Organism,
    Organismprop,
    Pub,
    PubDbxref,
)
from machado.views.search import (
    FeatureSearchView,
    FeatureSearchExportView,
    _doi_titles,
    _excluded_organism_names,
    _selected_facets_without_checkbox,
)
from machado.searchindex import build_organism
from machado.tests.searchindex_fixture import build_search_index_fixture
from unittest.mock import patch, MagicMock
from django.template.loader import render_to_string


class SearchFacetTemplateTest(TestCase):
    """A facet with a single option offers no real choice; its card is skipped."""

    def _render(self, fields, doi_titles=None):
        return render_to_string(
            "search_facet.html",
            {
                "query": "",
                "selected_facets": [],
                "facets": {"fields": fields},
                "facet_fields_order": list(fields.keys()),
                "facet_fields_desc": {k: k for k in fields},
                "doi_titles": doi_titles or {},
            },
        )

    def test_single_option_facet_is_hidden(self):
        """A facet field with exactly one value renders no card."""
        html = self._render({"orthology": [(False, 100)]})
        self.assertNotIn("Orthology", html)

    def test_multi_option_facet_is_shown(self):
        """A facet field with more than one value still renders its card."""
        html = self._render({"organism": [("Bos taurus", 50), ("Homo sapiens", 30)]})
        self.assertIn("Organism", html)

    def test_doi_facet_shows_title_when_known(self):
        """A DOI with a known publication title displays the title, not the raw DOI."""
        html = self._render(
            {"doi": [("10.1234/has-title", 5), ("10.5555/other", 1)]},
            doi_titles={"10.1234/has-title": "A Great Paper About Kinases"},
        )
        self.assertIn("A Great Paper About Kinases", html)
        self.assertIn('value="doi:10.1234/has-title"', html)

    def test_selection_without_a_checkbox_is_carried_as_hidden_input(self):
        """A selection the form cannot show must still be submitted.

        Selecting a facet usually narrows its own card to a single value,
        and single-option cards are not rendered -- so the checkbox that
        carried the selection disappears. The facet form is separate from
        the search form, so pressing "Apply Filters" then submits only what
        this form holds, silently dropping the selection. A hidden input
        keeps it.
        """
        html = render_to_string(
            "search_facet.html",
            {
                # A non-empty selection renders the "Selected filters" card,
                # whose remove links need the request in context.
                "request": RequestFactory().get("/find/"),
                "query": "",
                "selected_facets": ["organism:Zea mays"],
                "unrendered_selected_facets": ["organism:Zea mays"],
                "facets": {"fields": {"so_term": [("gene", 3), ("mRNA", 2)]}},
                "facet_fields_order": ["organism", "so_term"],
                "facet_fields_desc": {"organism": "organism", "so_term": "so_term"},
                "doi_titles": {},
            },
        )
        self.assertIn(
            '<input type="hidden" name="selected_facets" value="organism:Zea mays">',
            html,
        )
        # A multi-line {# #} is not a comment in Django -- it renders verbatim.
        self.assertNotIn('Apply Filters" would submit', html)
        self.assertNotIn("{#", html)

    def test_doi_facet_falls_back_to_doi_when_title_unknown(self):
        """A DOI with no known title falls back to displaying the raw DOI."""
        html = self._render(
            {"doi": [("10.5555/no-title", 2), ("10.1234/has-title", 1)]},
            doi_titles={"10.1234/has-title": "A Great Paper About Kinases"},
        )
        self.assertIn("10.5555/no-title", html)


class DoiTitlesTest(TestCase):
    """_doi_titles must map DOI accession strings to their publication title."""

    def setUp(self):
        """Create a Pub with a title and a DOI dbxref pointing at it."""
        db_doi = Db.objects.create(name="DOI")
        self.dbxref_doi = Dbxref.objects.create(
            db=db_doi, accession="10.1234/example", version="1"
        )

        cv = Cv.objects.create(name="pub_type")
        db_local = Db.objects.create(name="local")
        type_dbxref = Dbxref.objects.create(db=db_local, accession="journal")
        pub_type = Cvterm.objects.create(
            cv=cv,
            name="journal",
            dbxref=type_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        self.pub = Pub.objects.create(
            uniquename="PUB:1", type=pub_type, title="A great paper about kinases"
        )
        PubDbxref.objects.create(pub=self.pub, dbxref=self.dbxref_doi, is_current=True)

    def test_maps_known_doi_to_title(self):
        """A DOI with a matching PubDbxref resolves to that Pub's title."""
        titles = _doi_titles(["10.1234/example"])
        self.assertEqual(titles, {"10.1234/example": "A great paper about kinases"})

    def test_ignores_unknown_doi(self):
        """A DOI with no matching PubDbxref is simply absent from the result."""
        titles = _doi_titles(["10.1234/example", "10.9999/unknown"])
        self.assertEqual(titles, {"10.1234/example": "A great paper about kinases"})

    def test_empty_input_makes_no_query(self):
        """An empty input list returns an empty dict without querying the DB."""
        self.assertEqual(_doi_titles([]), {})


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

    def test_empty_arrays_do_not_change_the_counts(self):
        """Rows with an empty array contribute nothing and are skipped.

        _compute_array_facet filters them out with ``<> '[]'`` so the
        partial index on the column is usable. That is only sound because
        unnesting an empty array yields no rows, so the counts must come out
        identical whether or not such rows exist -- which is what this pins.
        """
        qs = FeatureSearchIndex.objects.all()
        before = dict(FeatureSearchView._compute_array_facet(qs, "analyses"))

        org = Organism.objects.get(genus="Gen", species="spec")
        cvterm = Cvterm.objects.get(name="gene")
        for i in range(4):
            feature = Feature.objects.create(
                organism=org,
                uniquename=f"empty_feature_{i}",
                type=cvterm,
                is_analysis=False,
                is_obsolete=False,
                timeaccessioned="2023-01-01T00:00:00Z",
                timelastmodified="2023-01-01T00:00:00Z",
            )
            FeatureSearchIndex.objects.create(feature=feature, analyses=[])

        after = dict(FeatureSearchView._compute_array_facet(qs, "analyses"))
        self.assertEqual(before, after)
        self.assertNotIn("", after, "an empty array leaked in as a facet value")

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


@override_settings(MACHADO_VALID_TYPES=["gene", "mRNA", "polypeptide"])
class FacetCountMatchesFilterTest(TestCase):
    """A facet's count must equal the number of rows selecting it returns.

    This is the promise a faceted UI makes: the number beside a facet value
    is how many results clicking it yields. Asserted over every facet the
    view publishes rather than one field, so a facet whose count is computed
    by a different rule than the filter it applies cannot pass silently --
    which is exactly how orthologs_coexpression came to advertise more hits
    than the table has rows while returning none of them.
    """

    def setUp(self):
        """Index the shared fixture corpus so the facets have real counts."""
        build_search_index_fixture()
        call_command("rebuild_search_index", batch_size=50, verbosity=0)

    def _run(self, **params):
        """Return (facet fields, result queryset) for a /find/ request."""
        request = RequestFactory().get("/find/", params)
        request.user = AnonymousUser()
        view = FeatureSearchView()
        view.request = request
        view.args = ()
        view.kwargs = {}
        view.object_list = view.get_queryset()
        context = view.get_context_data(object_list=view.object_list)
        return context["facets"]["fields"], view.object_list

    def test_every_facet_count_matches_its_filtered_result_count(self):
        """Selecting a facet returns exactly as many rows as its count."""
        facets, _ = self._run()

        checked = 0
        for field, pairs in facets.items():
            for value, count in pairs:
                _, qs = self._run(selected_facets="{}:{}".format(field, value))
                self.assertEqual(
                    qs.count(),
                    count,
                    "facet {}:{} advertises {} results but returns {}".format(
                        field, value, count, qs.count()
                    ),
                )
                checked += 1

        self.assertTrue(checked, "the fixture produced no facet values to check")


class OrganismExclusionQuerysetTest(TestCase):
    """The organism exclusion must be applied only when it can match.

    ``exclude(organism__in=names)`` is equivalent to no filter at all when
    no indexed row carries one of those names -- but it is not free:
    reading ``organism`` to evaluate it stops every facet aggregate from
    running as an index-only scan over its own field, which measured 4.90s
    instead of 0.64s for the seven scalar facets on a 7.5M-row index. So
    the predicate is dropped when nothing matches, and these tests pin both
    halves of that: dropped when it cannot match, kept when it can.
    """

    def setUp(self):
        """Create one hidden and one visible organism, both with index rows."""
        db = Db.objects.create(name="local")
        cv_seq = Cv.objects.create(name="sequence")
        gene_dbxref = Dbxref.objects.create(db=db, accession="gene")
        self.gene = Cvterm.objects.create(
            cv=cv_seq,
            name="gene",
            dbxref=gene_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # multispecies is hidden from every user, authenticated or not.
        self.hidden = Organism.objects.get(genus="multispecies", species="multispecies")
        self.visible = Organism.objects.create(genus="Arabidopsis", species="thaliana")

    def _index(self, organism, uniquename):
        feature = Feature.objects.create(
            organism=organism,
            uniquename=uniquename,
            type=self.gene,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned="2023-01-01T00:00:00Z",
            timelastmodified="2023-01-01T00:00:00Z",
        )
        return FeatureSearchIndex.objects.create(
            feature=feature,
            uniquename=uniquename,
            organism=build_organism(organism),
            so_term="gene",
        )

    def _queryset(self):
        request = RequestFactory().get("/find/")
        request.user = AnonymousUser()
        view = FeatureSearchView()
        view.request = request
        view.args = ()
        view.kwargs = {}
        return view.get_queryset()

    def test_exclusion_is_dropped_when_no_indexed_row_matches(self):
        """With no hidden organism indexed, no organism predicate is emitted."""
        self._index(self.visible, "VISIBLE_1")

        sql = str(self._queryset().query)
        self.assertNotIn(
            "multispecies",
            sql,
            "the exclusion was still applied even though nothing can match it",
        )

    def test_hidden_organism_is_excluded_when_it_has_indexed_rows(self):
        """A hidden organism with index rows is kept out of the results."""
        self._index(self.visible, "VISIBLE_1")
        self._index(self.hidden, "HIDDEN_1")

        names = set(self._queryset().values_list("uniquename", flat=True))
        self.assertIn("VISIBLE_1", names)
        self.assertNotIn(
            "HIDDEN_1",
            names,
            "a hidden organism leaked into the results",
        )


class SelectedFacetsWithoutCheckboxTest(TestCase):
    """Which selections the filter form cannot represent as a checkbox."""

    def test_collapsed_card_needs_a_hidden_input(self):
        """A facet narrowed to one value renders no card, so no checkbox."""
        facets = {
            "organism": [("Zea mays", 5)],
            "so_term": [("gene", 3), ("mRNA", 2)],
        }
        self.assertEqual(
            _selected_facets_without_checkbox(facets, ["organism:Zea mays"]),
            ["organism:Zea mays"],
        )

    def test_multi_value_card_keeps_its_own_checkbox(self):
        """A card still offering a choice carries the selection itself."""
        facets = {"so_term": [("gene", 3), ("mRNA", 2)]}
        self.assertEqual(
            _selected_facets_without_checkbox(facets, ["so_term:gene"]), []
        )

    def test_boolean_values_match_regardless_of_case(self):
        """Facet values arrive as bools; selections arrive as querystring text.

        The template writes them inconsistently -- "false" for orthology but
        "False" for orthologs_coexpression -- so neither casing may be
        treated as missing, or the filter would be submitted twice.
        """
        facets = {"orthology": [(False, 3), (True, 2)]}
        for value in ("true", "True", "false", "False"):
            self.assertEqual(
                _selected_facets_without_checkbox(facets, [f"orthology:{value}"]),
                [],
                f"orthology:{value} was treated as having no checkbox",
            )

    def test_value_missing_from_a_rendered_card_needs_a_hidden_input(self):
        """A card lists at most 100 values; a selection outside them has none."""
        facets = {"orthologous_group": [("OG_1", 4), ("OG_2", 2)]}
        self.assertEqual(
            _selected_facets_without_checkbox(facets, ["orthologous_group:OG_999"]),
            ["orthologous_group:OG_999"],
        )

    def test_value_containing_a_colon_is_not_split_apart(self):
        """Only the first colon separates field from value; DOIs contain them."""
        facets = {"doi": [("10.1234/a:b", 2), ("10.5555/c", 1)]}
        self.assertEqual(
            _selected_facets_without_checkbox(facets, ["doi:10.1234/a:b"]), []
        )

    def test_facet_absent_from_the_page_needs_a_hidden_input(self):
        """A selection whose field produced no facet at all is still kept."""
        self.assertEqual(
            _selected_facets_without_checkbox({}, ["organism:Zea mays"]),
            ["organism:Zea mays"],
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

        self.public_org = Organism.objects.create(
            genus="Arabidopsis", species="thaliana"
        )
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
        mock_qs.values.return_value.annotate.return_value.order_by.side_effect = (
            lambda f: [{f: "val", "count": 1}]
        )
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
