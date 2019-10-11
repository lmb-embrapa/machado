# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from django.core.exceptions import ObjectDoesNotExist

from haystack.query import SearchQuerySet

from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from machado.api.serializers import JBrowseFeatureSerializer
from machado.api.serializers import JBrowseGlobalSerializer
from machado.api.serializers import JBrowseNamesSerializer
from machado.api.serializers import JBrowseRefseqSerializer
from machado.api.serializers import autocompleteSerializer
from machado.loaders.common import retrieve_organism
from machado.models import Feature, Featureloc

from re import escape, search, IGNORECASE

class StandardResultSetPagination(PageNumberPagination):
    """Set the pagination parameters."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class JBrowseGlobalViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to view JBrowse global settings."""

    renderer_classes = (JSONRenderer,)

    def list(self, request):
        """List."""
        data = {"featureDensity": 0.02}
        serializer = JBrowseGlobalSerializer(data)
        return Response(serializer.data)


class JBrowseNamesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to JBrowse names."""

    renderer_classes = (JSONRenderer,)

    serializer_class = JBrowseNamesSerializer

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
            queryset = None

        return queryset


class JBrowseRefSeqsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to JBrowse refSeqs.json."""

    renderer_classes = (JSONRenderer,)
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

    renderer_classes = (JSONRenderer,)
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
                end = self.request.query_params.get("end", refseq.seqlen)

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


class autocompleteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to provide autocomplete hits."""

    renderer_classes = (JSONRenderer,)
    serializer_class = autocompleteSerializer

    def get_queryset(self):
        """Get queryset."""
        max_items = 10
        request = self.request
        query = request.GET.get('q')
        if query is not None:
            query = query.strip()
            queryset = SearchQuerySet().filter(autocomplete=query)[:max_items*10]
            result = set()
            for item in queryset:
                try:
                    aux = list()
                    for i in query.split(" "):
                        regex = r"\w*" + escape(i) + "\w*"
                        aux.append(search(regex, item.autocomplete, IGNORECASE).group())
                    result.add(" ".join(aux))
                except AttributeError:
                    pass
            return list(result)[:max_items]
        else:
         return None
