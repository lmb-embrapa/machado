"""Load relations ontology."""

import obonet
from chado.loaders.common import Validator
from chado.loaders.ontology import Ontology
from tqdm import tqdm


class RelationOntologyLoader(object):
    """Load relations ontology."""

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

        cv_name = 'relationship'

        # Initializing ontology
        ontology = Ontology(cv_name)

        # Load typedefs as Dbxrefs and Cvterm
        if self.verbosity > 0:
            self.stdout.write('Loading typedefs')

        for data in tqdm(G.graph['typedefs']):
            ontology.store_type_def(data)
