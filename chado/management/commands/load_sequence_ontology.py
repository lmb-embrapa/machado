"""Load Sequence Ontology."""

from chado.loaders.common import Validator
from chado.loaders.ontology import OntologyLoader
from django.core.management.base import BaseCommand
from tqdm import tqdm
import obonet


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
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        file = options.get('so')

        Validator().validate(file)

        # Load the ontology file
        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        if verbosity > 0:
            self.stdout.write('Preprocessing')

        cv_name = G.graph['default-namespace'][0]
        cv_definition = G.graph['data-version']

        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)

        if verbosity > 0:
            self.stdout.write('Loading typedefs')

        # Load typedefs as Dbxrefs and Cvterm
        for typedef in tqdm(G.graph['typedefs']):
            ontology.store_type_def(typedef)

        if verbosity > 0:
            self.stdout.write('Loading terms')

        for n, data in tqdm(G.nodes(data=True)):
            ontology.store_term(n, data)

        if verbosity > 0:
            self.stdout.write('Loading relationships')

        for u, v, type in tqdm(G.edges(keys=True)):
            ontology.store_relationship(u, v, type)

        self.stdout.write(self.style.SUCCESS('Done'))
