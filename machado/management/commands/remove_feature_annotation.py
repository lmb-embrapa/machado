# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove feature annotation."""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from machado.loaders.common import retrieve_organism
from machado.models import Cvterm, Featureprop, History


class Command(BaseCommand):
    """Remove organism."""

    help = "Remove organism"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--organism",
            help="Species name (eg. Homo sapiens, Mus musculus)",
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
        history_obj = History()
        history_obj.start(command="remove_feature_annotation", params=locals())
        try:
            cvterm_obj = Cvterm.objects.get(name=cvterm, cv__name="feature_property")
        except ObjectDoesNotExist:
            history_obj.failure(description="cvterm does not exist in the database")
            raise CommandError("cvterm does not exist in database!")

        try:
            organism_obj = retrieve_organism(organism)
            feature_props = Featureprop.objects.filter(
                type=cvterm_obj, feature__organism=organism_obj
            )
        except (ObjectDoesNotExist, AttributeError):
            feature_props = Featureprop.objects.filter(type=cvterm_obj)

        count = feature_props.count()
        feature_props.delete()

        history_obj.success(description="{} removed".format(count))
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("{} removed".format(count)))
