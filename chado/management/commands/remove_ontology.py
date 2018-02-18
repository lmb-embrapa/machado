"""Remove ontology."""

from chado.models import Cv, Cvterm
from chado.models import CvtermDbxref, Cvtermprop
from chado.models import Cvtermsynonym, CvtermRelationship
from chado.models import Dbxref
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class Command(BaseCommand):
    """Remove ontology."""

    help = 'Remove Ontology (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="cv.name", required=True, type=str)

    def handle(self, name: str, **options):
        """Execute the main function."""
        try:
            cv = Cv.objects.get(name=name)

            self.stdout.write(
                    'Deleting {} and every child record (CASCADE)'
                    .format(name))

            cvterm_ids = Cvterm.objects.filter(cv=cv).values_list('cvterm_id',
                                                                  flat=True)
            dbxref_ids = CvtermDbxref.objects.filter(
                cvterm_id__in=cvterm_ids).values_list('dbxref_id', flat=True)
            CvtermDbxref.objects.filter(cvterm_id__in=cvterm_ids).delete()
            Cvtermsynonym.objects.filter(cvterm_id__in=cvterm_ids).delete()
            Cvtermprop.objects.filter(cvterm_id__in=cvterm_ids).delete()
            CvtermRelationship.objects.filter(
                object_id__in=cvterm_ids).delete()
            CvtermRelationship.objects.filter(
                subject_id__in=cvterm_ids).delete()
            Cvterm.objects.filter(cvterm_id__in=cvterm_ids).delete()
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()

            dbxref_ids = Cvterm.objects.filter(
                cv=cv).values_list('dbxref_id', flat=True)
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()

            cv.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except IntegrityError as e:
            raise CommandError(
                    'It\'s not possible to delete every record. You must '
                    'delete ontologies loaded after \'{}\' that might depend '
                    'on it. {}'.format(name, e))
        except ObjectDoesNotExist:
            raise CommandError(
                    'Cannot remove \'{}\' (not registered)'.format(name))
