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

from rest_framework import views, viewsets, mixins, status
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


class JBrowseGlobalViewSet(views.APIView):
    """API endpoint to view JBrowse global settings."""

    def get(self, request):
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
        description="species",
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
        manual_parameters=[organism_param, equals_param, startswith_param]
    )
    def list(self, request):
        """List."""
        queryset = self.get_queryset()
        serializer = JBrowseNamesSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Get queryset."""
        try:
            organism = retrieve_organism(self.request.query_params.get("organism"))
        except (ObjectDoesNotExist, AttributeError):
            return

        queryset = Feature.objects.filter(organism=organism, is_obsolete=0).only(
            "feature_id"
        )

        equals = self.request.query_params.get("equals")
        startswith = self.request.query_params.get("startswith")
        if equals is not None:
            queryset = queryset.filter(uniquename=equals)
        elif startswith is not None:
            queryset = queryset.filter(uniquename__startswith=startswith)
        else:
            queryset = queryset

        return queryset


class JBrowseRefSeqsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to JBrowse refSeqs.json."""

    serializer_class = JBrowseRefseqSerializer

    def get_queryset(self):
        """Get queryset."""
        try:
            organism = retrieve_organism(self.request.query_params.get("organism"))
        except (ObjectDoesNotExist, AttributeError):
            return

        try:
            queryset = Feature.objects.filter(
                organism=organism,
                is_obsolete=0,
                type__cv__name="sequence",
                type__name=self.request.query_params.get("soType"),
            )
        except ObjectDoesNotExist:
            return

        return queryset


class JBrowseFeatureViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to view gene."""

    serializer_class = JBrowseFeatureSerializer

    def get_serializer_context(self):
        """Get the serializer context."""
        refseq_feature_obj = (
            Feature.objects.filter(uniquename=self.kwargs.get("refseq"))
            .only("feature_id")
            .first()
        )
        soType = self.request.query_params.get("soType")
        return {"refseq": refseq_feature_obj, "soType": soType}

    def get_queryset(self):
        """Get queryset."""
        try:
            refseq = (
                Feature.objects.filter(uniquename=self.kwargs.get("refseq"))
                .only("feature_id")
                .first()
            )
        except ObjectDoesNotExist:
            return

        soType = self.request.query_params.get("soType")
        if soType is None:
            queryset = list()
            queryset.append(refseq)
            return queryset
        else:
            try:
                organism = retrieve_organism(self.request.query_params.get("organism"))
            except (ObjectDoesNotExist, AttributeError):
                return

            try:
                soType = self.request.query_params.get("soType")
                start = self.request.query_params.get("start", 1)
                end = self.request.query_params.get("end", len(refseq.seq))

                features_locs = Featureloc.objects.filter(srcfeature=refseq)
                if end is not None:
                    features_locs = features_locs.filter(fmin__lte=end)
                features_locs = features_locs.filter(fmax__gte=start)
                features_ids = features_locs.values_list("feature_id", flat=True)

                return Feature.objects.filter(
                    type__cv__name="sequence",
                    type__name=soType,
                    organism=organism,
                    is_obsolete=0,
                    feature_id__in=features_ids,
                ).only("feature_id")

            except ObjectDoesNotExist:
                return None

    def list(self, request, *args, **kwargs):
        """Override return the list inside a dict."""
        response = super(JBrowseFeatureViewSet, self).list(request, *args, **kwargs)
        response.data = {"features": response.data}
        return response


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

    @swagger_auto_schema(manual_parameters=[q_param])
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

    def list(self, request, *args, **kwargs):
        """Retrieve ortholog group by feature ID."""
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


class FeatureSequenceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Retrieve sequence by feature ID."""

    serializer_class = FeatureSequenceSerializer

    def get_queryset(self):
        """Get queryset."""
        try:
            return Feature.objects.filter(feature_id=self.kwargs.get("feature_id"))
        except ObjectDoesNotExist:
            return


class FeaturePublicationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Retrieve publication by feature ID."""

    serializer_class = FeaturePublicationSerializer

    def get_queryset(self):
        """Get queryset."""
        try:
            return Pub.objects.filter(
                FeaturePub_pub_Pub__feature__feature_id=self.kwargs.get("feature_id")
            )
        except ObjectDoesNotExist:
            return
