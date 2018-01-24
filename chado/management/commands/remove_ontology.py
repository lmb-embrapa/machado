"""Remove ontology."""
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv, Cvterm
from chado.models import CvtermDbxref, Cvtermprop
from chado.models import Cvtermsynonym, CvtermRelationship
from chado.models import Dbxref


class Command(BaseCommand):
    """Remove ontology."""

    help = 'Remove Ontology (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="cv.name", required=True, type=str)

    def handle(self, *args, **options):
        """Execute the main function."""
        try:
            cv = Cv.objects.get(name=options['name'])

            self.stdout.write('Deleting %s and every child record (CASCADE)'
                              % (options['name']))

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
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Cannot remove %s (not registered)' % (options['name'])))
