# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from machado.models import Analysis, Analysisfeature
from machado.models import Cv, Cvterm, Db, Dbxref, Feature, Organism
from machado.serializers import AnalysisSerializer, AnalysisfeatureSerializer
from machado.serializers import CvSerializer, CvtermSerializer
from machado.serializers import DbSerializer, DbxrefSerializer
from machado.serializers import FeatureSerializer, OrganismSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
import django_filters


class StandardResultSetPagination(PageNumberPagination):
    """Set the pagination parameters."""

    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


def index(request):
    """Index."""
    return HttpResponse('Hello, world.')


def stats(request):
    """General stats."""
    data = dict()

    try:
        cvs = Cvterm.objects.values(key=F('cv__name'))
        cvs = cvs.values('key')
        cvs = cvs.annotate(count=Count('key'))
        cvs = cvs.filter(count__gt=5)
        cvs = cvs.order_by('key')
        if cvs:
            data.update({'Controlled vocabularies': cvs})
    except ObjectDoesNotExist:
        pass

    try:
        chr_cvterm = Cvterm.objects.get(
            cv__name='sequence', name='chromosome')
        chrs = Feature.objects.filter(type_id=chr_cvterm.cvterm_id)
        chrs = chrs.annotate(key=Concat(
            'organism__genus', Value(' '), 'organism__species'))
        chrs = chrs.values('key')
        chrs = chrs.annotate(count=Count('key'))
        if chrs:
            data.update({'Chromosomes': chrs})
    except ObjectDoesNotExist:
        pass

    try:
        scaff_cvterm = Cvterm.objects.get(
            cv__name='sequence', name='assembly')
        scaffs = Feature.objects.filter(type_id=scaff_cvterm.cvterm_id)
        scaffs = scaffs.annotate(key=Concat(
            'organism__genus', Value(' '), 'organism__species'))
        scaffs = scaffs.values('key')
        scaffs = scaffs.annotate(count=Count('key'))
        if scaffs:
            data.update({'Scaffolds': scaffs})
    except ObjectDoesNotExist:
        pass

    try:
        gene_cvterm = Cvterm.objects.get(
            cv__name='sequence', name='gene')
        genes = Feature.objects.filter(type_id=gene_cvterm.cvterm_id)
        genes = genes.annotate(key=Concat(
            'organism__genus', Value(' '), 'organism__species'))
        genes = genes.values('key')
        genes = genes.annotate(count=Count('key'))
        if genes:
            data.update({'Genes': genes})
    except ObjectDoesNotExist:
        pass

    try:
        protein_cvterm = Cvterm.objects.get(
            cv__name='sequence', name='polypeptide')
        proteins = Feature.objects.filter(type_id=protein_cvterm.cvterm_id)
        proteins = proteins.annotate(key=Concat(
            'organism__genus', Value(' '), 'organism__species'))
        proteins = proteins.values('key')
        proteins = proteins.annotate(count=Count('key'))
        if proteins:
            data.update({'Proteins': proteins})
    except ObjectDoesNotExist:
        pass

    return render(request, 'stats.html', {'context': data})


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
