# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove organism."""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from machado.models import Organism


class Command(BaseCommand):
    """Remove organism."""

    help = "Remove organism"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--genus", help="genus", required=True, type=str)
        parser.add_argument("--species", help="species", required=True, type=str)

    def handle(self, genus: str, species: str, verbosity: int = 1, **options):
        """Execute the main function."""
        try:
            organism = Organism.objects.get(species=species, genus=genus)
            if organism:
                organism.delete()
                if verbosity > 0:
                    self.stdout.write(
                        self.style.SUCCESS("{} {} removed".format(genus, species))
                    )

        except ObjectDoesNotExist:
            raise CommandError("Organism does not exist in database!")
