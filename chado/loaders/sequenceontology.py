"""Load Sequence Ontology."""
from chado.loaders.common import Validator
from chado.loaders.ontology import Ontology
from tqdm import tqdm
import obonet


class SequenceOntologyLoader(object):
    """Load Sequence Ontology."""

    def __init__(self, verbosity, stdout):
        """Initialization."""
        self.verbosity = verbosity
        self.stdout = stdout

    def handle(self, file):
        """Execute the main function."""
        Validator().validate(file)

        # Load the ontology file
        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        if self.verbosity > 0:
            self.stdout.write('Preprocessing')

        cv_name = G.graph['default-namespace'][0]
        cv_definition = G.graph['data-version']

        # Initializing ontology
        ontology = Ontology(cv_name, cv_definition)

        if self.verbosity > 0:
            self.stdout.write('Loading typedefs')

        # Load typedefs as Dbxrefs and Cvterm
        for typedef in tqdm(G.graph['typedefs']):
            ontology.store_type_def(typedef)

        if self.verbosity > 0:
            self.stdout.write('Loading terms')

        for n, data in tqdm(G.nodes(data=True)):
            ontology.store_term(n, data)

        if self.verbosity > 0:
            self.stdout.write('Loading relationships')

        for u, v, type in tqdm(G.edges(keys=True)):
            ontology.store_relationship(u, v, type)
