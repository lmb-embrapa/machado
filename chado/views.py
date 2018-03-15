"""Views."""

from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render

from chado.models import Cvterm, Feature


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
