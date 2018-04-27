# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove publication."""
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Pub, PubDbxref, Dbxref


class Command(BaseCommand):
    """Remove publication."""

    help = 'Remove publication'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--doi",
                            help="doi",
                            required=True,
                            type=str)

    def handle(self, doi: str, **options):
        """Execute the main function."""
        try:
            dbxref = Dbxref.objects.get(accession=doi)
            pub_dbxref = PubDbxref.objects.get(dbxref_id=dbxref.dbxref_id)
            pub = Pub.objects.get(pub_id=pub_dbxref.pub_id)
            # pub_author = Pubauthor.objects.get(pub_id=pub.pub_id)
            if dbxref and pub_dbxref and pub:
                pub.delete()
                self.stdout.write(self.style.SUCCESS(
                    '{} removed'.format(doi)))

        except ObjectDoesNotExist:
                raise CommandError('DOI does not exist in database!')
