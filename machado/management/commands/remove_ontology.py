# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove ontology."""

from machado.models import (
    Cv,
    Cvterm,
    CvtermDbxref,
    Cvtermprop,
    Cvtermsynonym,
    CvtermRelationship,
    Dbxref,
)
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from machado.management.commands._base import HistoryCommandMixin
from django.db.utils import IntegrityError


class Command(HistoryCommandMixin, BaseCommand):
    """Remove ontology."""

    help = "Remove an ontology and all its associated terms from the database (CASCADE)"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--name",
            help="Name of the ontology (cv.name) to remove",
            required=True,
            action="append",
        )

    def handle(self, name: list, verbosity: int = 1, **options):
        """Execute the main function."""
        for n in name:
            try:
                cv = Cv.objects.get(name=n)
                if verbosity > 0:
                    self.stdout.write(
                        "Deleting ontology '{}' and all associated terms...".format(n)
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
                    self.stdout.write(
                        self.style.SUCCESS(
                            "Operation completed successfully for '{}'.".format(n)
                        )
                    )
            except IntegrityError as e:
                raise CommandError(
                    "Unable to delete records. Please ensure that any ontologies "
                    "dependent on '{}' are removed first. Error: {}".format(n, e)
                )
            except ObjectDoesNotExist:
                raise CommandError(
                    "Cannot remove '{}' (not found in database).".format(n)
                )
