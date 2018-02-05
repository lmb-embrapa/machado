"""Load Gene Ontology."""

from chado.loaders.common import Validator
from chado.loaders.ontology import OntologyLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from multiprocessing import Lock
from obonet import read_obo
from tqdm import tqdm


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

        Validator().validate(file)

        # Load the ontology file
        with open(file) as obo_file:
            G = read_obo(obo_file)

        cv_definition = G.graph['date']

        if verbosity > 0:
            self.stdout.write('Preprocessing')

        # Instantiating Ontology in order to have access to secondary cv, db,
        # cvterm, and dbxref, even though the main cv will not be used.
        # There will be a ontology for each namespace, plus one called
        # gene_ontology for storing type_defs
        ontology = OntologyLoader('biological_process', cv_definition)
        ontology = OntologyLoader('molecular_function', cv_definition)
        ontology = OntologyLoader('cellular_component', cv_definition)
        ontology = OntologyLoader('external', cv_definition)
        ontology = OntologyLoader('gene_ontology', cv_definition)

        # Load typedefs as Dbxrefs and Cvterm
        if verbosity > 0:
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
        if verbosity > 0:
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
        if verbosity > 0:
            self.stdout.write(
                'Loading relationships ({} threads)'.format(cpu))

        tasks = list()
        for u, v, type in G.edges(keys=True):
            tasks.append(pool.submit(
                ontology.store_relationship, u, v, type))
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        self.stdout.write(self.style.SUCCESS('Done'))
