"""Remove organism."""
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Organism


class Command(BaseCommand):
    """Remove organism."""

    help = 'Remove organism'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--genus",
                            help="genus",
                            required=True,
                            type=str)
        parser.add_argument("--species",
                            help="species",
                            required=True,
                            type=str)

    def handle(self, genus: str, species: str, **options):
        """Execute the main function."""
        try:
            organism = Organism.objects.get(species=species, genus=genus)
            if organism:
                organism.delete()
                self.stdout.write(self.style.SUCCESS(
                    '{} {} removed'.format(genus, species)))

        except ObjectDoesNotExist:
                raise CommandError('Organism does not exist in database!')
