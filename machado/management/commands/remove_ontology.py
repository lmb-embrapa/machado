# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove ontology."""

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from machado.models import Cv, Cvterm
from machado.models import CvtermDbxref, Cvtermprop
from machado.models import Cvtermsynonym, CvtermRelationship
from machado.models import Dbxref


class Command(BaseCommand):
    """Remove ontology."""

    help = "Remove Ontology (CASCADE)"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="cv.name", required=True, type=str)

    def handle(self, name: str, verbosity: int = 1, **options):
        """Execute the main function."""
        try:
            cv = Cv.objects.get(name=name)
            if verbosity > 0:
                self.stdout.write(
                    "Deleting {} and every child record (CASCADE)".format(name)
                )
            cvterm_ids = list(
                Cvterm.objects.filter(cv=cv).values_list("cvterm_id", flat=True)
            )
            dbxref_ids = list(
                CvtermDbxref.objects.filter(cvterm_id__in=cvterm_ids).values_list(
                    "dbxref_id", flat=True
                )
            )
            CvtermDbxref.objects.filter(cvterm_id__in=cvterm_ids).delete()
            Cvtermsynonym.objects.filter(cvterm_id__in=cvterm_ids).delete()
            Cvtermprop.objects.filter(cvterm_id__in=cvterm_ids).delete()
            CvtermRelationship.objects.filter(object_id__in=cvterm_ids).delete()
            CvtermRelationship.objects.filter(subject_id__in=cvterm_ids).delete()
            Cvterm.objects.filter(cvterm_id__in=cvterm_ids).delete()
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()

            dbxref_ids = list(
                Cvterm.objects.filter(cv=cv).values_list("dbxref_id", flat=True)
            )
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()

            cv.delete()

            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS("Done"))
        except IntegrityError as e:
            raise CommandError(
                "It's not possible to delete every record. You must "
                "delete ontologies loaded after '{}' that might depend "
                "on it. {}".format(name, e)
            )
        except ObjectDoesNotExist:
            raise CommandError("Cannot remove '{}' (not registered)".format(name))
