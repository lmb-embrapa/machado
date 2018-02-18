"""Load relations ontology."""

from chado.loaders.common import FileValidator
from chado.loaders.exceptions import ImportingError
from chado.loaders.ontology import OntologyLoader
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import obonet


class Command(BaseCommand):
    """Load relations ontology."""

    help = 'Load Relations Ontology'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="Relations Ontology file obo. "
                            "Available at https://github.com/oborel/"
                            "obo-relations", required=True, type=str)

    def handle(self, file: str, verbosity: int=1, **options):
        """Execute the main function."""
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        # Load the ontology file
        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        if verbosity > 0:
            self.stdout.write('Preprocessing')

        cv_name = 'relationship'

        # Initializing ontology
        ontology = OntologyLoader(cv_name)

        # Load typedefs as Dbxrefs and Cvterm
        if verbosity > 0:
            self.stdout.write('Loading typedefs')

        for data in tqdm(G.graph['typedefs']):
            ontology.store_type_def(data)

        self.stdout.write(self.style.SUCCESS('Done'))
