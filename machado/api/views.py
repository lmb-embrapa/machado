# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature, Featureloc
from machado.api.serializers import CvSerializer, CvtermSerializer
from machado.api.serializers import DbSerializer, DbxrefSerializer
from machado.api.serializers import OrganismSerializer
from machado.api.serializers import JBrowseFeatureSerializer
from machado.api.serializers import JBrowseNamesSerializer
from machado.api.serializers import JBrowseGlobalSerializer
from machado.api.serializers import JBrowseRefseqSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from rest_framework import viewsets, filters
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


class JBrowseGlobalViewSet(viewsets.ViewSet):
    """API endpoint to view JBrowse global settings."""

    renderer_classes = (JSONRenderer, )

    def list(self, request):
        """List."""
        data = {
            'featureDensity': 0.02
        }
        serializer = JBrowseGlobalSerializer(data)
        return Response(serializer.data)


class JBrowseNamesViewSet(viewsets.ReadOnlyModelViewSet):
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


class JBrowseRefSeqsViewSet(viewsets.ReadOnlyModelViewSet):
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


class JBrowseFeatureViewSet(viewsets.ReadOnlyModelViewSet):
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
            transcriptsloc = transcriptsloc.filter(fmin__lte=end)
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
