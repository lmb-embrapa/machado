# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Insert organism."""

from django.core.management.base import BaseCommand, CommandError

from machado.loaders.common import insert_organism
from machado.loaders.exceptions import ImportingError


class Command(BaseCommand):
    """Insert organism."""

    help = "Insert organism"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--abbreviation", help="abbreviation", required=False, type=str
        )
        parser.add_argument("--genus", help="genus", required=True, type=str)
        parser.add_argument("--species", help="species", required=True, type=str)
        parser.add_argument(
            "--common_name", help="common name", required=False, type=str
        )
        parser.add_argument(
            "--infraspecific_name", help="infraspecific name", required=False, type=str
        )
        parser.add_argument("--comment", help="comment", required=False, type=str)

    def handle(
        self,
        genus: str,
        species: str,
        abbreviation: str = None,
        common_name: str = None,
        infraspecific_name: str = None,
        comment: str = None,
        verbosity: int = 1,
        **options
    ) -> None:
        """Execute the main function."""
        try:
            insert_organism(
                genus=genus,
                species=species,
                abbreviation=abbreviation,
                common_name=common_name,
                infraspecific_name=infraspecific_name,
                comment=comment,
            )
        except ImportingError as e:
            raise CommandError(e)

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("{} {} registered".format(genus, species))
            )
