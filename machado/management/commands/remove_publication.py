# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove publication."""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from machado.models import Pub, PubDbxref, Dbxref


class Command(BaseCommand):
    """Remove publication."""

    help = "Remove publication"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--doi", help="doi", required=True, type=str)

    def handle(self, doi: str, verbosity: int = 1, **options):
        """Execute the main function."""
        try:
            dbxref = Dbxref.objects.get(accession=doi)
            pub_dbxref = PubDbxref.objects.get(dbxref=dbxref)
            Pub.objects.get(pub_id=pub_dbxref.pub_id).delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS("{} removed".format(doi)))
        except ObjectDoesNotExist:
            raise CommandError("DOI does not exist in database!")
