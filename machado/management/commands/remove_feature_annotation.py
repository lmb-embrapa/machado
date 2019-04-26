# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove feature annotation."""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from machado.loaders.common import retrieve_organism
from machado.models import Cvterm, Featureprop


class Command(BaseCommand):
    """Remove organism."""

    help = "Remove organism"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--organism",
            help="Species name (eg. Homo " "sapiens, Mus musculus)",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--cvterm",
            help="cvterm.name from cv "
            "feature_property. (eg. display, note, product, "
            "alias, ontology_term)",
            required=True,
            type=str,
        )

    def handle(self, cvterm: str, organism: str = None, verbosity: int = 1, **options):
        """Execute the main function."""
        try:
            cvterm_obj = Cvterm.objects.get(name=cvterm, cv__name="feature_property")
        except ObjectDoesNotExist:
            raise CommandError("cvterm does not exist in database!")

        try:
            organism_obj = retrieve_organism(organism)
            feature_props = Featureprop.objects.filter(
                type=cvterm_obj, feature__organism=organism_obj
            )
        except ObjectDoesNotExist:
            feature_props = Featureprop.objects.filter(type=cvterm_obj)

        count = feature_props.count()
        feature_props.delete()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("{} removed".format(count)))
