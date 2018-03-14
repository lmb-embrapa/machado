"""Views."""

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

from chado.models import Cvterm, Feature


def index(request):
    """Index."""
    return HttpResponse('Hello, world.')


def stats(request):
    """General stats."""
    cv = Cvterm.objects.values('cv__name')
    cv = cv.annotate(Count('cv_id'))
    cv = cv.filter(cv_id__count__gt=5)
    cv = cv.order_by('cv__name')

    chr_cvterm = Cvterm.objects.get(cv__name='sequence', name='chromosome')
    chrs = Feature.objects.values('organism__genus', 'organism__species')
    chrs = chrs.filter(type_id=chr_cvterm.cvterm_id)
    chrs = chrs.annotate(Count('organism_id'))

    scaff_cvterm = Cvterm.objects.get(cv__name='sequence', name='assembly')
    scaffs = Feature.objects.values('organism__genus', 'organism__species')
    scaffs = scaffs.filter(type_id=scaff_cvterm.cvterm_id)
    scaffs = scaffs.annotate(Count('organism_id'))

    gene_cvterm = Cvterm.objects.get(cv__name='sequence', name='gene')
    genes = Feature.objects.values('organism__genus', 'organism__species')
    genes = genes.filter(type_id=gene_cvterm.cvterm_id)
    genes = genes.annotate(Count('organism_id'))

    data = {
        'Controled vocabularies': cv,
        'Chromosomes': chrs,
        'Scaffolds': scaffs,
        'Genes': genes,
    }

    return render(request, 'stats.html', {'context': data})
