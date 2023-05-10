# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Check IDs."""

from django.core.exceptions import ObjectDoesNotExist
from machado.loaders.common import retrieve_feature_id, FileValidator, retrieve_organism
from machado.loaders.exceptions import ImportingError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Check IDs."""

    help = "Check IDs"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="File containing a list of IDs in the first column.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Species name (eg. Homo sapiens, Mus musculus)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--soterm",
            help="SO Sequence Ontology Term (eg. chromosome, assembly)",
            required=True,
            type=str,
        )

    def handle(
        self, file: str, organism: str, soterm: str, verbosity: int = 1, **options
    ) -> None:
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Loading")

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        try:
            organism = retrieve_organism(organism)
        except ImportingError as e:
            raise CommandError(e)
        f = open(file, "r+")
        for line in f.readlines():
            accession = line.split()[0]
            try:
                retrieve_feature_id(
                    accession=accession, soterm=soterm, organism=organism
                )
                continue
            except ObjectDoesNotExist:
                self.stdout.write(f"{accession} not found\n")
        f.close()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
