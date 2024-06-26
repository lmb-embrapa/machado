# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""common views."""

from django.conf import settings
from django.db.models import Count
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from machado.models import Cv, Organism, Feature, Pub


class HomeView(TemplateView):
    """Home view."""

    template_name = "index.html"


class CongratsView(TemplateView):
    """Congrats view."""

    def get(self, request):
        """General data numbers."""
        data = dict()

        data["cv"] = Cv.objects.count()
        data["organism"] = Organism.objects.count()
        data["feature"] = Feature.objects.count()
        data["pub"] = Pub.objects.count()

        return render(request, "congrats.html", {"context": data})


class DataSummaryView(View):
    """Summary views."""

    def get(self, request):
        """General data numbers."""
        data = dict()

        if hasattr(settings, "MACHADO_VALID_TYPES"):
            counts = (
                Feature.objects.filter(
                    type__name__in=settings.MACHADO_VALID_TYPES,
                    type__cv__name="sequence",
                )
                .values(
                    "organism__genus",
                    "organism__species",
                    "organism__infraspecific_name",
                    "type__name",
                )
                .annotate(count=Count("type__name"))
                .order_by(
                    "organism__genus",
                    "organism__species",
                    "organism__infraspecific_name",
                )
            )
        else:
            counts = (
                Feature.objects.filter(type__cv__name="sequence")
                .values(
                    "organism__genus",
                    "organism__species",
                    "organism__infraspecific_name",
                    "type__name",
                )
                .annotate(count=Count("type__name"))
                .order_by(
                    "organism__genus",
                    "organism__species",
                    "organism__infraspecific_name",
                )
            )

        for item in counts:
            organism_name = "{} {} {}".format(
                item["organism__genus"],
                item["organism__species"],
                (
                    item["organism__infraspecific_name"]
                    if item["organism__infraspecific_name"] is not None
                    else ""
                ),
            )
            data.setdefault(organism_name, {}).setdefault("counts", []).append(item)

        for key, value in data.items():
            organism = key.split()
            genus = organism[0]
            species = organism[1]
            try:
                infraspecific_name = organism[2]
            except IndexError:
                infraspecific_name = ""

            pubs = Pub.objects.filter(
                OrganismPub_pub_Pub__organism__genus=genus,
                OrganismPub_pub_Pub__organism__species=species,
                OrganismPub_pub_Pub__organism__infraspecific_name=infraspecific_name,
            )
            if pubs:
                data[key].update({"pubs": pubs})

        return render(request, "data-numbers.html", {"context": data})
