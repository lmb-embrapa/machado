"""Remove organisms file."""
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Db, Dbxref, Organism, Organismprop, OrganismDbxref


class Command(BaseCommand):
    """Remove organisms file."""

    help = 'Remove organisms file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--dbname",
                            help="Organism DB name",
                            required=True,
                            type=str)

    def handle(self, dbname: str, **options):
        """Execute the main function."""
        try:
            db = Db.objects.get(name=dbname)
            dbxref_ids = list(Dbxref.objects.filter(
                db=db).values_list('dbxref_id', flat=True))
            organism_ids = list(OrganismDbxref.objects.filter(
                dbxref_id__in=dbxref_ids).values_list(
                    'organism_id', flat=True))
            Organismprop.objects.filter(organism_id__in=organism_ids).delete()
            OrganismDbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()
            Organism.objects.filter(organism_id__in=organism_ids).delete()
            Dbxref.objects.filter(db=db).delete()
            db.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Cannot remove {} (not registered)'.format(dbname))
