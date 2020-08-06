# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from django.core.exceptions import ObjectDoesNotExist

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from haystack.query import SearchQuerySet

from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from machado.api.serializers import JBrowseFeatureSerializer
from machado.api.serializers import JBrowseNamesSerializer
from machado.api.serializers import JBrowseRefseqSerializer
from machado.api.serializers import autocompleteSerializer
from machado.api.serializers import FeatureOrthologSerializer
from machado.api.serializers import FeaturePublicationSerializer
from machado.api.serializers import FeatureSequenceSerializer
from machado.loaders.common import retrieve_organism
from machado.models import Feature, Featureloc, Featureprop, Pub

from re import escape, search, IGNORECASE


class StandardResultSetPagination(PageNumberPagination):
    """Set the pagination parameters."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class JBrowseGlobalViewSet(viewsets.GenericViewSet):
    """API endpoint to view JBrowse global settings."""

    @swagger_auto_schema(
        operation_summary="Retrieve global settings",
        operation_description="Retrieve global settings. https://jbrowse.org/docs/data_formats.html",
    )
    def list(self, request):
        """List."""
        result = {"featureDensity": 0.02}
        response = Response(result, status=status.HTTP_200_OK)
        return response


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
    def list(self, request, *args, **kwargs):
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

        return queryset


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
    def list(self, request, *args, **kwargs):
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


class autocompleteViewSet(viewsets.GenericViewSet):
    """API endpoint to provide autocomplete hits."""

    serializer_class = autocompleteSerializer

    q_param = openapi.Parameter(
        "q",
        openapi.IN_QUERY,
        description="search string",
        required=False,
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        manual_parameters=[q_param],
        operation_summary="Search the ElasticSearch index for matching strings",
        operation_description="Search the ElasticSearch index for matching strings.",
    )
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


class FeatureOrthologViewSet(viewsets.GenericViewSet):
    """API endpoint for feature ortholog."""

    serializer_class = FeatureOrthologSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve ortholog group by feature ID",
        operation_description="Retrieve ortholog group by feature ID.",
    )
    def list(self, request, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeatureOrthologSerializer(queryset, many=True)
        try:
            ortholog_group = Featureprop.objects.get(
                type__name="orthologous group",
                type__cv__name="feature_property",
                feature_id=self.kwargs.get("feature_id"),
            ).value
            return Response(
                {"ortholog_group": ortholog_group, "members": serializer.data}
            )
        except ObjectDoesNotExist:
            return Response()

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


class FeatureSequenceViewSet(viewsets.GenericViewSet):
    """Retrieve sequence by feature ID."""

    serializer_class = FeatureSequenceSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve sequence by feature ID",
        operation_description="Retrieve sequence by feature ID.",
    )
    def list(self, request, *args, **kwargs):
        """List."""
        queryset = self.get_queryset()
        serializer = FeaturePublicationSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        try:
            return Feature.objects.filter(feature_id=self.kwargs.get("feature_id"))
        except ObjectDoesNotExist:
            return


class FeaturePublicationViewSet(viewsets.GenericViewSet):
    """Retrieve publication by feature ID."""

    serializer_class = FeaturePublicationSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve publication by feature ID",
        operation_description="Retrieve publication by feature ID.",
    )
    def list(self, request, *args, **kwargs):
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
