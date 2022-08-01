# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from haystack.query import SearchQuerySet

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from machado.api.serializers import JBrowseFeatureSerializer
from machado.api.serializers import JBrowseGlobalSerializer
from machado.api.serializers import JBrowseNamesSerializer
from machado.api.serializers import JBrowseRefseqSerializer
from machado.api.serializers import autocompleteSerializer
from machado.api.serializers import FeatureCoexpressionSerializer
from machado.api.serializers import FeatureExpressionSerializer
from machado.api.serializers import FeatureIDSerializer
from machado.api.serializers import FeatureInfoSerializer
from machado.api.serializers import FeatureLocationSerializer
from machado.api.serializers import FeatureOntologySerializer
from machado.api.serializers import FeatureOrthologSerializer
from machado.api.serializers import FeatureProteinMatchesSerializer
from machado.api.serializers import FeaturePublicationSerializer
from machado.api.serializers import FeatureSequenceSerializer
from machado.api.serializers import FeatureSimilaritySerializer
from machado.loaders.common import retrieve_organism, retrieve_feature_id
from machado.models import Analysis, Analysisfeature, Cvterm, Pub
from machado.models import Feature, Featureloc, Featureprop, FeatureRelationship

from re import escape, search, IGNORECASE


try:
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 60 * 60


class StandardResultSetPagination(PageNumberPagination):
    """Set the pagination parameters."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class JBrowseGlobalViewSet(viewsets.GenericViewSet):
    """API endpoint to view JBrowse global settings."""

    serializer_class = JBrowseGlobalSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve global settings",
        operation_description="Retrieve global settings. https://jbrowse.org/docs/data_formats.html",
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, request):
        """List."""
        queryset = self.get_queryset()
        serializer = JBrowseGlobalSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        return [{"featureDensity": 0.02}]

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(JBrowseGlobalViewSet, self).dispatch(*args, **kwargs)


class JBrowseNamesViewSet(viewsets.GenericViewSet):
    """API endpoint to JBrowse names."""

    serializer_class = JBrowseNamesSerializer

    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name",
        required=True,
        type=openapi.TYPE_STRING,
    )
    equals_param = openapi.Parameter(
        "equals",
        openapi.IN_QUERY,
        description="exact matching string",
        required=False,
        type=openapi.TYPE_STRING,
    )
    startswith_param = openapi.Parameter(
        "startswith",
        openapi.IN_QUERY,
        description="starts with matching string",
        required=False,
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        manual_parameters=[organism_param, equals_param, startswith_param],
        operation_summary="Retrieve feature names by accession",
        operation_description="Retrieve feature names by accession. https://jbrowse.org/docs/data_formats.html",
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, request):
        """List."""
        queryset = self.get_queryset()
        serializer = JBrowseNamesSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        queryset = (
            Feature.objects.filter(is_obsolete=0)
            .exclude(name=None)
            .exclude(uniquename=None)
        )

        organism = self.request.query_params.get("organism")

        if organism is not None:
            queryset = queryset.filter(organism=retrieve_organism(organism))

        equals = self.request.query_params.get("equals")
        startswith = self.request.query_params.get("startswith")
        if startswith is not None:
            return queryset.filter(uniquename__startswith=startswith)
        elif equals is not None:
            return queryset.filter(uniquename=equals)
        else:
            return queryset

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(JBrowseNamesViewSet, self).dispatch(*args, **kwargs)


class JBrowseRefSeqsViewSet(viewsets.GenericViewSet):
    """API endpoint to JBrowse refSeqs.json."""

    serializer_class = JBrowseRefseqSerializer

    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name",
        required=True,
        type=openapi.TYPE_STRING,
    )
    sotype_param = openapi.Parameter(
        "soType",
        openapi.IN_QUERY,
        description="Sequence Ontology term",
        required=True,
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        manual_parameters=[sotype_param, organism_param],
        operation_summary="Retrieve reference sequences",
        operation_description="Retrieve reference sequences. https://jbrowse.org/docs/data_formats.html",
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = JBrowseRefseqSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        organism = self.request.query_params.get("organism")
        sotype = self.request.query_params.get("soType")

        queryset = Feature.objects.filter(is_obsolete=0)
        if organism is not None:
            queryset = queryset.filter(organism=retrieve_organism(organism))
        if sotype is not None:
            queryset = queryset.filter(type__cv__name="sequence", type__name=sotype)

        queryset = queryset.only("seqlen", "uniquename")

        return queryset

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(JBrowseRefSeqsViewSet, self).dispatch(*args, **kwargs)


class JBrowseFeatureViewSet(viewsets.GenericViewSet):
    """API endpoint to view gene."""

    serializer_class = JBrowseFeatureSerializer

    start_param = openapi.Parameter(
        "start",
        openapi.IN_QUERY,
        description="start",
        required=False,
        type=openapi.TYPE_INTEGER,
    )
    end_param = openapi.Parameter(
        "end",
        openapi.IN_QUERY,
        description="start",
        required=False,
        type=openapi.TYPE_INTEGER,
    )
    sotype_param = openapi.Parameter(
        "soType",
        openapi.IN_QUERY,
        description="Sequence Ontology term",
        required=False,
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        manual_parameters=[sotype_param, start_param, end_param],
        operation_description="Retrieve features from reference sequence (refseq). https://jbrowse.org/docs/data_formats.html",
        operation_summary="Retrieve features from reference sequence",
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        serializer = JBrowseFeatureSerializer(queryset, context=context, many=True)
        return Response({"features": serializer.data})

    def get_serializer_context(self):
        """Get the serializer context."""
        refseq_feature_obj = Feature.objects.filter(
            uniquename=self.kwargs.get("refseq")
        ).first()
        soType = self.request.query_params.get("soType")
        return {"refseq": refseq_feature_obj, "soType": soType}

    def get_queryset(self, *args, **kwargs):
        """Get queryset."""
        try:
            refseq = Feature.objects.filter(
                uniquename=self.kwargs.get("refseq")
            ).first()

        except ObjectDoesNotExist:
            return

        try:
            soType = self.request.query_params.get("soType")
            start = self.request.query_params.get("start", 1)
            end = self.request.query_params.get("end")

            features_locs = Featureloc.objects.filter(srcfeature=refseq)
            if end is not None:
                features_locs = features_locs.filter(fmin__lte=end)
            features_locs = features_locs.filter(fmax__gte=start)
            features_ids = features_locs.values_list("feature_id", flat=True)

            features = Feature.objects.filter(
                feature_id__in=features_ids, is_obsolete=0
            )
            if soType is not None:
                features = features.filter(type__cv__name="sequence", type__name=soType)
            return features

        except ObjectDoesNotExist:
            return None

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(JBrowseFeatureViewSet, self).dispatch(*args, **kwargs)


class autocompleteViewSet(viewsets.GenericViewSet):
    """API endpoint to provide autocomplete hits."""

    serializer_class = autocompleteSerializer

    q_param = openapi.Parameter(
        "q",
        openapi.IN_QUERY,
        description="search string",
        required=True,
        type=openapi.TYPE_STRING,
    )

    operation_summary = "Search the ElasticSearch index for matching strings"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_TXT"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_TXT
        )

    @swagger_auto_schema(
        manual_parameters=[q_param],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, request):
        """Search the ElasticSearch index for matching strings."""
        queryset = self.get_queryset()
        serializer = autocompleteSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        max_items = 10
        request = self.request
        query = request.query_params.get("q")
        if query is not None:
            query = query.strip()
            queryset = SearchQuerySet().filter(autocomplete=query)[: max_items * 10]
            result = set()
            for item in queryset:
                try:
                    aux = list()
                    for i in query.split(" "):
                        regex = r"\w*" + escape(i) + r"\w*"
                        aux.append(search(regex, item.autocomplete, IGNORECASE).group())
                    result.add(" ".join(aux))
                except AttributeError:
                    pass
            return list(result)[:max_items]
        else:
            return None

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(autocompleteViewSet, self).dispatch(*args, **kwargs)


class FeatureIDViewSet(viewsets.GenericViewSet):
    """Retrieve the feature ID by accession."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureIDSerializer

    accession_param = openapi.Parameter(
        "accession",
        openapi.IN_QUERY,
        description="Feature name or accession",
        required=True,
        type=openapi.TYPE_STRING,
    )
    sotype_param = openapi.Parameter(
        "soType",
        openapi.IN_QUERY,
        description="Sequence Ontology term",
        required=True,
        type=openapi.TYPE_STRING,
    )

    operation_summary = "Retrieve feature ID by accession"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_AA_ACC"):
        operation_description += (
            "<b>Example:</b><br />accession={}, soType=polypeptide".format(
                settings.MACHADO_EXAMPLE_AA_ACC
            )
        )

    @swagger_auto_schema(
        manual_parameters=[accession_param, sotype_param],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, request):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureIDSerializer(queryset, many=False)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        accession = self.request.query_params.get("accession")
        soterm = self.request.query_params.get("soType")
        try:
            feature_id = retrieve_feature_id(accession, soterm)
            return {"feature_id": feature_id}
        except ObjectDoesNotExist:
            return None

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureIDViewSet, self).dispatch(*args, **kwargs)


class FeatureOrthologViewSet(viewsets.GenericViewSet):
    """API endpoint for feature ortholog."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureOrthologSerializer

    operation_summary = "Retrieve ortholog group by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_AA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_AA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureOrthologSerializer(queryset, many=True)
        try:
            feature_obj = Feature.objects.get(feature_id=self.kwargs.get("feature_id"))
            return Response(
                {
                    "ortholog_group": feature_obj.get_orthologous_group(),
                    "members": serializer.data,
                }
            )
        except ObjectDoesNotExist:
            return Response({"coexpression_group": None, "members": list()})

    def get_queryset(self):
        """Get queryset."""
        try:
            ortholog_group = Featureprop.objects.get(
                type__name="orthologous group",
                type__cv__name="feature_property",
                feature_id=self.kwargs.get("feature_id"),
            )
            return Feature.objects.filter(
                type__name="polypeptide",
                Featureprop_feature_Feature__value=ortholog_group.value,
            )
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureOrthologViewSet, self).dispatch(*args, **kwargs)


class FeatureCoexpressionViewSet(viewsets.GenericViewSet):
    """API endpoint for feature coexpression."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureOrthologSerializer

    operation_summary = "Retrieve co-expression group by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_NA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_NA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureCoexpressionSerializer(queryset, many=True)
        try:
            feature_obj = Feature.objects.get(feature_id=self.kwargs.get("feature_id"))
            return Response(
                {
                    "coexpression_group": feature_obj.get_coexpression_group(),
                    "members": serializer.data,
                }
            )
        except ObjectDoesNotExist:
            return Response({"coexpression_group": None, "members": list()})

    def get_queryset(self):
        """Get queryset."""
        try:
            coexpression_group = Featureprop.objects.get(
                type__name="coexpression group",
                type__cv__name="feature_property",
                feature_id=self.kwargs.get("feature_id"),
            )
            return Feature.objects.filter(
                type__name="mRNA",
                Featureprop_feature_Feature__value=coexpression_group.value,
            )
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureCoexpressionViewSet, self).dispatch(*args, **kwargs)


class FeatureExpressionViewSet(viewsets.GenericViewSet):
    """API endpoint for feature expression."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureExpressionSerializer

    operation_summary = "Retrieve expression by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_NA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_NA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureExpressionSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        feature_id = self.kwargs.get("feature_id")
        try:
            feature_obj = Feature.objects.get(feature_id=feature_id)
            return feature_obj.get_expression_samples()
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureExpressionViewSet, self).dispatch(*args, **kwargs)


class FeatureInfoViewSet(viewsets.GenericViewSet):
    """API endpoint for feature info."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureInfoSerializer

    operation_summary = "Retrieve general information by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_NA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_NA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureInfoSerializer(queryset, many=False)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        try:
            return Feature.objects.get(feature_id=self.kwargs.get("feature_id"))
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureInfoViewSet, self).dispatch(*args, **kwargs)


class FeatureLocationViewSet(viewsets.GenericViewSet):
    """Retrieve location by feature ID."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureLocationSerializer

    operation_summary = "Retrieve location by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_NA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_NA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureLocationSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        feature_id = self.kwargs.get("feature_id")
        try:
            feature_obj = Feature.objects.get(feature_id=feature_id)
            return feature_obj.get_location()
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureLocationViewSet, self).dispatch(*args, **kwargs)


class FeatureSequenceViewSet(viewsets.GenericViewSet):
    """Retrieve sequence by feature ID."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureSequenceSerializer

    operation_summary = "Retrieve sequence by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_NA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_NA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureSequenceSerializer(queryset, many=False)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        try:
            return Feature.objects.get(feature_id=self.kwargs.get("feature_id"))
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureSequenceViewSet, self).dispatch(*args, **kwargs)


class FeaturePublicationViewSet(viewsets.GenericViewSet):
    """Retrieve publication by feature ID."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeaturePublicationSerializer

    operation_summary = "Retrieve publication by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_NA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_NA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeaturePublicationSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        try:
            return Pub.objects.filter(
                FeaturePub_pub_Pub__feature__feature_id=self.kwargs.get("feature_id")
            )
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeaturePublicationViewSet, self).dispatch(*args, **kwargs)


class FeatureOntologyViewSet(viewsets.GenericViewSet):
    """Retrieve ontology terms by feature ID."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureOntologySerializer

    operation_summary = "Retrieve ontology terms by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_AA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_AA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureOntologySerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        try:
            return Cvterm.objects.filter(
                FeatureCvterm_cvterm_Cvterm__feature_id=self.kwargs.get("feature_id")
            )
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureOntologyViewSet, self).dispatch(*args, **kwargs)


class FeatureProteinMatchesViewSet(viewsets.GenericViewSet):
    """Retrieve protein matches by feature ID."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureProteinMatchesSerializer

    operation_summary = "Retrieve protein matches by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_AA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_AA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureProteinMatchesSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        try:
            return FeatureRelationship.objects.filter(
                object_id=self.kwargs.get("feature_id"),
                subject__type__name="protein_match",
                subject__type__cv__name="sequence",
            )
        except ObjectDoesNotExist:
            return

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureProteinMatchesViewSet, self).dispatch(*args, **kwargs)


class FeatureSimilarityViewSet(viewsets.GenericViewSet):
    """Retrieve similarity matches by feature ID."""

    lookup_field = "feature_id"
    lookup_value_regex = r"^\d+$"
    serializer_class = FeatureSimilaritySerializer

    operation_summary = "Retrieve similarity matches by feature ID"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_AA"):
        operation_description += "<b>Example:</b><br />feature_id={}".format(
            settings.MACHADO_EXAMPLE_AA
        )

    @swagger_auto_schema(
        operation_summary=operation_summary, operation_description=operation_description
    )
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def list(self, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureSimilaritySerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        result = list()
        srcfeature_id = self.kwargs.get("feature_id")
        try:
            match_parts_ids = Featureloc.objects.filter(
                srcfeature_id=srcfeature_id
            ).values_list("feature_id")
        except ObjectDoesNotExist:
            return list()

        for match_part_id in match_parts_ids:
            analysis_feature = Analysisfeature.objects.get(feature_id=match_part_id)
            analysis = Analysis.objects.get(analysis_id=analysis_feature.analysis_id)
            if analysis_feature.normscore is not None:
                score = analysis_feature.normscore
            else:
                score = analysis_feature.rawscore

            # it should have 2 records (query and hit)
            match_query = Featureloc.objects.filter(
                feature_id=match_part_id, srcfeature_id=srcfeature_id
            ).first()
            match_hit = (
                Featureloc.objects.filter(feature_id=match_part_id)
                .exclude(srcfeature_id=srcfeature_id)
                .first()
            )

            result.append(
                {
                    "program": analysis.program,
                    "programversion": analysis.programversion,
                    "db_name": match_hit.srcfeature.dbxref.db.name,
                    "unique": match_hit.srcfeature.uniquename,
                    "name": match_hit.srcfeature.name,
                    "sotype": match_query.srcfeature.type.name,
                    "query_start": match_query.fmin,
                    "query_end": match_query.fmax,
                    "score": score,
                    "evalue": analysis_feature.significance,
                }
            )

        return result

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super(FeatureSimilarityViewSet, self).dispatch(*args, **kwargs)
