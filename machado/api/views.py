# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.models import Cv, Cvterm, Db, Dbxref
from machado.models import Feature, Featureloc
from machado.api.serializers import CvSerializer, CvtermSerializer
from machado.api.serializers import DbSerializer, DbxrefSerializer
from machado.api.serializers import JBrowseFeatureSerializer
from machado.api.serializers import JBrowseNamesSerializer
from machado.api.serializers import JBrowseGlobalSerializer
from machado.api.serializers import JBrowseRefseqSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, filters, mixins
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class StandardResultSetPagination(PageNumberPagination):
    """Set the pagination parameters."""

    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CvViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Cv."""

    queryset = Cv.objects.all().order_by('name')
    serializer_class = CvSerializer
    pagination_class = StandardResultSetPagination


class CvtermViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Cvterm."""

    queryset = Cvterm.objects.all().order_by('name')
    serializer_class = CvtermSerializer
    pagination_class = StandardResultSetPagination


class NestedCvtermViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Cvterm."""

    queryset = Cvterm.objects.all()
    serializer_class = CvtermSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        try:
            cvterms = self.queryset.filter(cv=self.kwargs['cv_pk'])
        except KeyError:
            pass

        return cvterms


class DbViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Db."""

    queryset = Db.objects.all().order_by('name')
    serializer_class = DbSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description',)
    pagination_class = StandardResultSetPagination


class DbxrefViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Dbxref."""

    queryset = Dbxref.objects.all()
    queryset = queryset.order_by('accession')
    serializer_class = DbxrefSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('db__name', 'description',)
    pagination_class = StandardResultSetPagination


class NestedDbxrefViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Cvterm."""

    queryset = Dbxref.objects.all()
    serializer_class = DbxrefSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        try:
            dbxrefs = self.queryset.filter(db=self.kwargs['db_pk'])
        except KeyError:
            pass

        return dbxrefs


class JBrowseGlobalViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to view JBrowse global settings."""

    renderer_classes = (JSONRenderer, )

    def list(self, request):
        """List."""
        data = {
            'featureDensity': 0.02
        }
        serializer = JBrowseGlobalSerializer(data)
        return Response(serializer.data)


class JBrowseNamesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to JBrowse names."""

    renderer_classes = (JSONRenderer, )

    serializer_class = JBrowseNamesSerializer

    def get_queryset(self):
        """Get queryset."""
        try:
            organism = retrieve_organism(
                self.request.query_params.get('organism'))
        except (ObjectDoesNotExist, AttributeError):
            return

        queryset = Feature.objects.filter(organism=organism)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

        equals = self.request.query_params.get('equals')
        startswith = self.request.query_params.get('startswith')
        if equals is not None:
            queryset = queryset.filter(uniquename=equals)
        elif startswith is not None:
            queryset = queryset.filter(uniquename__startswith=startswith)
        else:
            queryset = None

        return queryset


class JBrowseRefSeqsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to JBrowse refSeqs.json."""

    renderer_classes = (JSONRenderer, )
    serializer_class = JBrowseRefseqSerializer

    def get_queryset(self):
        """Get queryset."""
        try:
            organism = retrieve_organism(
                self.request.query_params.get('organism'))
        except (ObjectDoesNotExist, AttributeError):
            return

        try:
            cvterm = Cvterm.objects.get(
                cv__name='sequence',
                name=self.request.query_params.get('soType'))
        except (ObjectDoesNotExist, AttributeError):
            return

        try:
            queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
            queryset = queryset.filter(organism=organism)
            queryset = queryset.filter(is_obsolete=0)
            queryset = queryset.order_by('uniquename')
        except ObjectDoesNotExist:
            return

        return queryset


class JBrowseFeatureViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint to view gene."""

    renderer_classes = (JSONRenderer, )
    serializer_class = JBrowseFeatureSerializer

    def get_serializer_context(self):
        """Get the serializer context."""
        cvterm_display = retrieve_ontology_term(ontology='feature_property',
                                                term='display')
        cvterm_part_of = retrieve_ontology_term(ontology='sequence',
                                                term='part_of')
        refseq_feature_id = Feature.objects.get(
            uniquename=self.kwargs['refseq'])
        return {
            'cvterm_display': cvterm_display,
            'cvterm_part_of': cvterm_part_of,
            'refseq': refseq_feature_id,
        }

    def get_queryset(self):
        """Get queryset."""
        soType = self.request.query_params.get('soType')
        try:
            refseq = Feature.objects.get(uniquename=self.kwargs['refseq'])
        except ObjectDoesNotExist:
            return

        try:
            organism = retrieve_organism(
                self.request.query_params.get('organism'))
        except (ObjectDoesNotExist, AttributeError):
            return

        try:
            soType = self.request.query_params.get('soType')
            start = self.request.query_params.get('start') or 1
            end = self.request.query_params.get('end') or refseq.seqlen

            if soType == "reference":
                queryset = list()
                queryset.append(refseq)
                return queryset

            cvterm = Cvterm.objects.get(cv__name='sequence', name=soType)

            queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
            queryset = queryset.filter(organism=organism)
            queryset = queryset.filter(is_obsolete=0)
            queryset = queryset.order_by('uniquename')

            transcriptsloc = Featureloc.objects.filter(srcfeature=refseq)
            if end is not None:
                transcriptsloc = transcriptsloc.filter(fmin__lte=end)
            if start is not None:
                transcriptsloc = transcriptsloc.filter(fmax__gte=start)
            transcript_ids = transcriptsloc.values_list('feature_id',
                                                        flat=True)

            queryset = queryset.filter(feature_id__in=transcript_ids)
        except ObjectDoesNotExist:
            pass

        return queryset

    def list(self, request, *args, **kwargs):
        """Override return the list inside a dict."""
        response = super(JBrowseFeatureViewSet,
                         self).list(request, *args, **kwargs)
        response.data = {"features": response.data}
        return response
