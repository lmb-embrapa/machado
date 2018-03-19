"""Views."""

from chado.models import Cv, Cvterm, Feature, Organism
from chado.serializers import CvSerializer, CvtermSerializer
from chado.serializers import OrganismSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination


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
    cvs = Cvterm.objects.values(key=F('cv__name'))
    cvs = cvs.values('key')
    cvs = cvs.annotate(count=Count('key'))
    cvs = cvs.filter(count__gt=5)
    cvs = cvs.order_by('key')

    chr_cvterm = Cvterm.objects.get(cv__name='sequence', name='chromosome')
    chrs = Feature.objects.filter(type_id=chr_cvterm.cvterm_id)
    chrs = chrs.annotate(key=Concat(
        'organism__genus', Value(' '), 'organism__species'))
    chrs = chrs.values('key')
    chrs = chrs.annotate(count=Count('key'))

    scaff_cvterm = Cvterm.objects.get(cv__name='sequence', name='assembly')
    scaffs = Feature.objects.filter(type_id=scaff_cvterm.cvterm_id)
    scaffs = scaffs.annotate(key=Concat(
        'organism__genus', Value(' '), 'organism__species'))
    scaffs = scaffs.values('key')
    scaffs = scaffs.annotate(count=Count('key'))

    gene_cvterm = Cvterm.objects.get(cv__name='sequence', name='gene')
    genes = Feature.objects.filter(type_id=gene_cvterm.cvterm_id)
    genes = genes.annotate(key=Concat(
        'organism__genus', Value(' '), 'organism__species'))
    genes = genes.values('key')
    genes = genes.annotate(count=Count('key'))

    data = {
        'Controled vocabularies': cvs,
        'Chromosomes': chrs,
        'Scaffolds': scaffs,
        'Genes': genes,
    }

    return render(request, 'stats.html', {'context': data})


class CvViewSet(viewsets.ModelViewSet):
    """API endpoint to view Cv."""

    queryset = Cv.objects.all().order_by('name')
    serializer_class = CvSerializer
    pagination_class = StandardResultSetPagination


class CvtermViewSet(viewsets.ModelViewSet):
    """API endpoint to view Cvterm."""

    queryset = Cvterm.objects.all().order_by('name')
    serializer_class = CvtermSerializer
    pagination_class = StandardResultSetPagination


class NestedCvtermViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view Cvterm."""

    queryset = Cvterm.objects.all()
    serializer_class = CvtermSerializer

    def get_queryset(self):
        """Get queryset."""
        cvterms = Cvterm.objects.all()

        try:
            cvterms = self.queryset.filter(cv=self.kwargs['cv_pk'])
        except KeyError:
            pass

        return cvterms


class OrganismViewSet(viewsets.ModelViewSet):
    """API endpoint to view Organisms."""

    try:
        cvterm_species = Cvterm.objects.get(cv__name='taxonomy',
                                            name='species')
        queryset = Organism.objects.filter(type_id=cvterm_species.cvterm_id)
    except ObjectDoesNotExist:
        queryset = Organism.objects.all()

    serializer_class = OrganismSerializer
    pagination_class = StandardResultSetPagination
