"""Load Gene Ontology."""

from chado.loaders.common import Validator
from chado.loaders.ontology import Ontology
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Lock
from obonet import read_obo
from tqdm import tqdm


class GeneOntologyLoader(object):
    """Load Gene Ontology."""

    def __init__(self, verbosity, stdout):
        """Initialization."""
        self.verbosity = verbosity
        self.stdout = stdout

    def handle(self, file, cpu=1):
        """Execute the main function."""
        Validator().validate(file)

        # Load the ontology file
        with open(file) as obo_file:
            G = read_obo(obo_file)

        cv_definition = G.graph['date']

        if self.verbosity > 0:
            self.stdout.write('Preprocessing')

        # Instantiating Ontology in order to have access to secondary cv, db,
        # cvterm, and dbxref, even though the main cv will not be used.
        ontology = Ontology('biological_process', cv_definition)
        ontology = Ontology('molecular_function', cv_definition)
        ontology = Ontology('cellular_component', cv_definition)
        ontology = Ontology('external', cv_definition)

        # Load typedefs as Dbxrefs and Cvterm
        if self.verbosity > 0:
            self.stdout.write(
                'Loading typedefs ({} threads)'.format(cpu))

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for typedef in G.graph['typedefs']:
            tasks.append(pool.submit(ontology.store_type_def, typedef))
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        # Load the cvterms
        if self.verbosity > 0:
            self.stdout.write(
                'Loading terms ({} threads)'.format(cpu))

        lock = Lock()
        tasks = list()
        for n, data in G.nodes(data=True):
            tasks.append(pool.submit(
                ontology.store_term, n, data, lock))
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        # Load the relationship between cvterms
        if self.verbosity > 0:
            self.stdout.write(
                'Loading relationships ({} threads)'.format(cpu))

        tasks = list()
        for u, v, type in G.edges(keys=True):
            tasks.append(pool.submit(
                ontology.store_relationship, u, v, type))
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
