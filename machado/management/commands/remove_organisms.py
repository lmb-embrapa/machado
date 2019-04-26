# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove organisms file."""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from machado.models import Db, Dbxref, Organism, OrganismDbxref


class Command(BaseCommand):
    """Remove organisms file."""

    help = "Remove organisms file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--dbname", help="Organism DB name", required=True, type=str
        )

    def handle(self, dbname: str, verbosity: int = 1, **options):
        """Execute the main function."""
        try:
            db = Db.objects.get(name=dbname)
            dbxref_ids = list(
                Dbxref.objects.filter(db=db).values_list("dbxref_id", flat=True)
            )
            organism_ids = list(
                OrganismDbxref.objects.filter(dbxref_id__in=dbxref_ids).values_list(
                    "organism_id", flat=True
                )
            )
            Organism.objects.filter(organism_id__in=organism_ids).delete()
            Dbxref.objects.filter(db=db).delete()
            db.delete()

            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS("Done"))
        except ObjectDoesNotExist:
            raise CommandError("Cannot remove {} (not registered)".format(dbname))
