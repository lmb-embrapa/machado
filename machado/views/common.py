# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""common views."""

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from machado.models import Cvterm, Feature, Organism


def index(request):
    """Index."""
    if request.GET.get('current_organism_id') is not None:
        try:
            organism_obj = Organism.objects.get(
                organism_id=request.GET.get('current_organism_id'))
            request.session['current_organism_id'] = request.GET.get(
                'current_organism_id')
            request.session['current_organism_name'] = '{} {}'.format(
                organism_obj.genus, organism_obj.species)
        except (ObjectDoesNotExist, ValueError):
            request.session['current_organism_id'] = None
            request.session['current_organism_name'] = None

    if 'current_organism_id' not in request.session:
        request.session['current_organism_id'] = None
        request.session['current_organism_name'] = None

    if request.session.get('current_organism_id') is None:
        data = 'Hello, world.'
        return render(request, 'index.html', {'context': data})
    else:
        return render(request, 'query.html')


def data_numbers(request):
    """General data numbers."""
    data = dict()
    current_organism_id = request.session.get('current_organism_id')

    if current_organism_id is None:
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
        if current_organism_id is not None:
            chrs = chrs.filter(organism_id=current_organism_id)
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
        if current_organism_id is not None:
            scaffs = scaffs.filter(organism_id=current_organism_id)
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
        if current_organism_id is not None:
            genes = genes.filter(organism_id=current_organism_id)
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
        if current_organism_id is not None:
            proteins = proteins.filter(organism_id=current_organism_id)
        proteins = proteins.annotate(key=Concat(
            'organism__genus', Value(' '), 'organism__species'))
        proteins = proteins.values('key')
        proteins = proteins.annotate(count=Count('key'))
        if proteins:
            data.update({'Proteins': proteins})
    except ObjectDoesNotExist:
        pass

    return render(request, 'data-numbers.html', {'context': data})
