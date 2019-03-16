# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""common views."""

from django.shortcuts import render
from django.db.models import Count
from django.views import View
from django.views.generic import TemplateView
from machado.models import Feature, Organism, Pub


class HomeView(TemplateView):
    """Home view."""

    template_name = "index.html"


class DataSummaryView(View):
    """Summary views."""

    def get(self, request):
        """General data numbers."""
        data = dict()

        VALID_TYPES = ['chromosome', 'assembly', 'gene', 'mRNA', 'polypeptide']

        organism_objs = Organism.objects.order_by('genus', 'species')
        for organism_obj in organism_objs:
            organism_name = "{} {}".format(
                organism_obj.genus, organism_obj.species)

            counts = Feature.objects.filter(
                type__name__in=VALID_TYPES,
                type__cv__name='sequence',
                organism=organism_obj).values('type__name').annotate(
                    count=Count('type__name'))
            if counts:
                data[organism_name] = {'counts': counts}
                pubs = Pub.objects.filter(
                    OrganismPub_pub_Pub__organism=organism_obj)
                if pubs:
                    data[organism_name].update({'pubs': pubs})

        return render(request, 'data-numbers.html', {'context': data})
