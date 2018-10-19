# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from machado.models import Analysis, Analysisfeature
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature, Featureloc
from machado.api.serializers import AnalysisSerializer
from machado.api.serializers import AnalysisfeatureSerializer
from machado.api.serializers import CvSerializer, CvtermSerializer
from machado.api.serializers import DbSerializer, DbxrefSerializer
from machado.api.serializers import FeatureSerializer, OrganismSerializer
from machado.api.serializers import JBrowseTranscriptSerializer
from machado.api.serializers import JBrowseNamesSerializer
from machado.api.serializers import JBrowseGlobalSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import django_filters


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


class OrganismViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Organisms."""

    try:
        cvterm_species = Cvterm.objects.get(cv__name='taxonomy',
                                            name='species')
        queryset = Organism.objects.filter(type_id=cvterm_species.cvterm_id)
        queryset = queryset.annotate(feats=Count('Feature_organism_Organism'))
        queryset = queryset.filter(feats__gt=0)
        queryset = queryset.order_by('genus', 'species')
    except ObjectDoesNotExist:
        queryset = Organism.objects.all()

    serializer_class = OrganismSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('genus', 'species')
    ordering_fields = ('genus', 'species')
    pagination_class = StandardResultSetPagination


class ChromosomeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view chromosomes."""

    if Cvterm.objects.filter(cv__name='sequence', name='chromosome').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='chromosome')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

    serializer_class = FeatureSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('uniquename', 'name')
    ordering_fields = ('uniquename', 'name')
    pagination_class = StandardResultSetPagination


class NestedChromosomeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view chromosomes."""

    if Cvterm.objects.filter(cv__name='sequence', name='chromosome').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='chromosome')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

    serializer_class = FeatureSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('uniquename', 'name')
    ordering_fields = ('uniquename', 'name')
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        try:
            queryset = self.queryset.filter(
                organism=self.kwargs['organism_pk'])
        except KeyError:
            pass

        return queryset


class ScaffoldViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view scaffold."""

    if Cvterm.objects.filter(cv__name='sequence', name='assembly').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='assembly')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

    serializer_class = FeatureSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('uniquename', 'name')
    ordering_fields = ('uniquename', 'name')
    pagination_class = StandardResultSetPagination


class NestedScaffoldViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view scaffold."""

    if Cvterm.objects.filter(cv__name='sequence', name='assembly').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='assembly')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

    serializer_class = FeatureSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('uniquename', 'name')
    ordering_fields = ('uniquename', 'name')
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        try:
            queryset = self.queryset.filter(
                organism=self.kwargs['organism_pk'])
        except KeyError:
            pass

        return queryset


class GeneViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view gene."""

    if Cvterm.objects.filter(cv__name='sequence', name='gene').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='gene')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

    serializer_class = FeatureSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('uniquename', 'name')
    ordering_fields = ('uniquename', 'name')
    pagination_class = StandardResultSetPagination


class NestedGeneViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view gene."""

    if Cvterm.objects.filter(cv__name='sequence', name='gene').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='gene')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

    serializer_class = FeatureSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('uniquename', 'name')
    ordering_fields = ('uniquename', 'name')
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        try:
            queryset = self.queryset.filter(
                organism=self.kwargs['organism_pk'])
        except KeyError:
            pass

        return queryset


class ProteinFilter(django_filters.FilterSet):
    """Protein filter class."""

    uniquename = django_filters.CharFilter(name='uniquename',
                                           lookup_expr='icontains')
    match_count = django_filters.NumberFilter(name='match_count',
                                              lookup_expr='exact',
                                              label='Match count')

    class Meta:
        """Meta."""

        model = Feature
        fields = ['uniquename', 'match_count']


class ProteinViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view protein."""

    if Cvterm.objects.filter(cv__name='sequence', name='polypeptide').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='polypeptide')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.annotate(
            match_count=Count('Featureloc_srcfeature_Feature'))
        queryset = queryset.order_by('uniquename')
    else:
        queryset = Feature.objects.none()

    serializer_class = FeatureSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.SearchFilter)
    filter_class = ProteinFilter
    pagination_class = StandardResultSetPagination


class NestedProteinViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view protein."""

    if Cvterm.objects.filter(cv__name='sequence', name='polypeptide').exists():
        cvterm = Cvterm.objects.get(cv__name='sequence', name='polypeptide')
        queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
        queryset = queryset.filter(is_obsolete=0)
        queryset = queryset.annotate(
            match_count=Count('Featureloc_srcfeature_Feature'))
        queryset = queryset.order_by('uniquename')
    else:
        queryset = Feature.objects.none()

    serializer_class = FeatureSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.SearchFilter)
    filter_class = ProteinFilter
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        try:
            queryset = self.queryset.filter(
                organism=self.kwargs['organism_pk'])
        except KeyError:
            pass

        return queryset


class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view analysis."""

    queryset = Analysis.objects.all()
    queryset = queryset.order_by('sourcename')

    serializer_class = AnalysisSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('sourcename', 'program')
    pagination_class = StandardResultSetPagination


class MatchesViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view analysis matches."""

    queryset = Analysisfeature.objects.all()
    serializer_class = AnalysisfeatureSerializer
    pagination_class = StandardResultSetPagination


class NestedMatchesViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view analysis matches."""

    queryset = Analysisfeature.objects.all()
    serializer_class = AnalysisfeatureSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        try:
            analysisfeatures = self.queryset.filter(
                analysis=self.kwargs['analysis_pk'])
        except KeyError:
            pass

        return analysisfeatures


class NestedJBrowseGlobalViewSet(viewsets.ViewSet):
    """API endpoint to view JBrowse global settings."""

    renderer_classes = (JSONRenderer, )

    def list(self, request, organism_pk=None):
        """List."""
        data = {
            'featureDensity': 0.02
        }
        serializer = JBrowseGlobalSerializer(data)
        return Response(serializer.data)


class NestedJBrowseNamesViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to JBrowse names."""

    renderer_classes = (JSONRenderer, )

    serializer_class = JBrowseNamesSerializer
    # pagination_class = StandardResultSetPagination

    def get_queryset(self):
        """Get queryset."""
        queryset = Feature.objects.filter(is_obsolete=0)
        queryset = queryset.order_by('uniquename')

        try:
            equals = self.request.query_params.get('equals')
            startswith = self.request.query_params.get('startswith')
            if equals is not None:
                queryset = queryset.filter(name=equals)
            if startswith is not None:
                queryset = queryset.filter(name__startswith=startswith)
        except KeyError:
            pass

        return queryset


class NestedJBrowseTranscriptViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view gene."""

    renderer_classes = (JSONRenderer, )
    serializer_class = JBrowseTranscriptSerializer

    def get_queryset(self):
        """Get queryset."""
        try:
            refseq = Feature.objects.get(uniquename=self.kwargs['refseq'])
        except ObjectDoesNotExist:
            return

        try:
            soType = self.request.query_params.get('soType')
            start = self.request.query_params.get('start') or 1
            end = self.request.query_params.get('end') or refseq.seqlen

            cvterm = Cvterm.objects.get(cv__name='sequence', name=soType)

            queryset = Feature.objects.filter(type_id=cvterm.cvterm_id)
            queryset = queryset.filter(is_obsolete=0)
            queryset = queryset.order_by('uniquename')

            transcriptsloc = Featureloc.objects.filter(srcfeature=refseq)
            transcriptsloc = transcriptsloc.filter(fmin__lte=end)
            transcriptsloc = transcriptsloc.filter(fmax__gte=start)
            transcript_ids = transcriptsloc.values_list('feature_id',
                                                        flat=True)

            queryset = queryset.filter(feature_id__in=transcript_ids)
            queryset = queryset.filter(organism=self.kwargs['organism_pk'])
        except ObjectDoesNotExist:
            pass

        return queryset

    def list(self, request, *args, **kwargs):
        """Override return the list inside a dict."""
        response = super(NestedJBrowseTranscriptViewSet,
                         self).list(request, *args, **kwargs)
        response.data = {"features": response.data}
        return response
