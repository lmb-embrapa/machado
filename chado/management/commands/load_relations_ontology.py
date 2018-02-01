"""Load relations ontology."""

from chado.loaders.exceptions import ImportingError
from chado.loaders.ontologyRelation import RelationOntologyLoader
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Load relations ontology."""

    help = 'Load Relations Ontology'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--ro", help="Relations Ontology file obo. "
                            "Available at https://github.com/oborel/"
                            "obo-relations", required=True, type=str)

    def handle(self, *args, **options):
        """Execute the main function."""
        file = options.get('ro')
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        try:
            importer = RelationOntologyLoader(verbosity, self.stdout)
            importer.handle(file)
        except ImportingError as e:
            raise CommandError(str(e))

        self.stdout.write(self.style.SUCCESS('Done'))
