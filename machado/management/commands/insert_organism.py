# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Insert organism."""

from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin

from machado.loaders.common import insert_organism


class Command(HistoryCommandMixin, BaseCommand):
    """Insert organism."""

    help = "Register a new organism in the database"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--abbreviation",
            help="Abbreviated name (e.g., 'H. sapiens')",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--genus", help="Genus name (e.g., 'Homo')", required=True, type=str
        )
        parser.add_argument(
            "--species", help="Species name (e.g., 'sapiens')", required=True, type=str
        )
        parser.add_argument(
            "--common_name",
            help="Common name of the organism",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--infraspecific_name",
            help="Infraspecific name (e.g., strain or subspecies)",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--comment", help="Additional comments or notes", required=False, type=str
        )

    def handle(
        self,
        genus: str,
        species: str,
        abbreviation: str = None,
        common_name: str = None,
        infraspecific_name: str = None,
        comment: str = None,
        verbosity: int = 1,
        **options,
    ) -> None:
        """Execute the main function."""
        insert_organism(
            genus=genus,
            species=species,
            abbreviation=abbreviation,
            common_name=common_name,
            infraspecific_name=infraspecific_name,
            comment=comment,
        )
        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully registered organism '{} {}'.".format(genus, species)
                )
            )
