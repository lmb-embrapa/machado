# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Views."""

from machado.models import Cvterm, Feature
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render


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
