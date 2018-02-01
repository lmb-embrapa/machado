"""Load Sequence Ontology."""

from chado.loaders.exceptions import ImportingError
from chado.loaders.sequenceontology import SequenceOntologyLoader
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Load sequence ontology."""

    help = 'Load Sequence Ontology'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--so", help="Sequence Ontology file obo."
                            "Available at https://github.com/"
                            "The-Sequence-Ontology/SO-Ontologies",
                            required=True, type=str)

    def handle(self, *args, **options):
        """Execute the main function."""
        file = options.get('so')
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        try:
            importer = SequenceOntologyLoader(verbosity, self.stdout)
            importer.handle(file)
        except ImportingError as e:
            raise CommandError(str(e))

        self.stdout.write(self.style.SUCCESS('Done'))
