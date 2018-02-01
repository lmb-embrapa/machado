"""Load Gene Ontology."""

from chado.loaders.exceptions import ImportingError
from chado.loaders.geneontology import GeneOntologyLoader
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Load gene ontology."""

    help = 'Load Gene Ontology'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--go", help="Gene Ontology file obo. Available "
                            "at http://www.geneontology.org/ontology/gene_ont"
                            "ology.obo", required=True, type=str)
        parser.add_argument("--cpu",
                            help="Number of threads",
                            default=1,
                            type=int)

    def handle(self, *args, **options):
        """Execute the main function."""
        file = options.get('go')
        cpu = options.get('cpu')
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        try:
            importer = GeneOntologyLoader(verbosity, self.stdout)
            importer.handle(file, cpu)
        except ImportingError as e:
            raise CommandError(str(e))

        self.stdout.write(self.style.SUCCESS('Done'))
