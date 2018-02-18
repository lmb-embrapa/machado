"""Insert organism."""

from django.core.management.base import BaseCommand, CommandError
from chado.loaders.common import insert_organism
from chado.loaders.exceptions import ImportingError


class Command(BaseCommand):
    """Insert organism."""

    help = 'Insert organism'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--abbreviation",
                            help="abbreviation",
                            required=False,
                            type=str)
        parser.add_argument("--genus",
                            help="genus",
                            required=True,
                            type=str)
        parser.add_argument("--species",
                            help="species",
                            required=True,
                            type=str)
        parser.add_argument("--common_name",
                            help="common name",
                            required=False,
                            type=str)
        parser.add_argument("--infraspecific_name",
                            help="infraspecific name",
                            required=False,
                            type=str)
        parser.add_argument("--type",
                            help="type (Organism_type_Cvterm)",
                            required=False,
                            type=str)
        parser.add_argument("--comment",
                            help="comment",
                            required=False,
                            type=str)

    def handle(self,
               genus: str,
               species: str,
               abbreviation: str=None,
               common_name: str=None,
               infraspecific_name: str=None,
               type: str=None,
               comment: str=None,
               **options):
        """Execute the main function."""
        try:
            insert_organism(genus,
                            species,
                            common_name,
                            infraspecific_name,
                            type,
                            comment)
        except ImportingError as e:
            raise CommandError(e)

        self.stdout.write(
            self.style.SUCCESS('{} {} registered'.format(genus, species)))
