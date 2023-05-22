# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Check IDs."""

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
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
            "--soterms",
            help="SO Sequence Ontology Terms (eg. gene, mRNA, miRNA)",
            required=True,
            nargs="+",
            type=str,
        )

    def handle(
        self, file: str, organism: str, soterms: list, verbosity: int = 1, **options
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
            notfound = set()
            accession = line.split()[0]
            for soterm in soterms:
                try:
                    retrieve_feature_id(
                        accession=accession, soterm=soterm, organism=organism
                    )
                    break
                except ObjectDoesNotExist:
                    notfound.add(soterm)
                except MultipleObjectsReturned:
                    self.stdout.write(f"{accession} matches to multiple records\n")
                    break
            if len(notfound) == len(soterms):
                self.stdout.write(f"{accession} {str(notfound)} not found\n")
        f.close()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
