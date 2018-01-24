"""Load Gene Ontology."""

from chado.lib.cvterm import get_cvterm, get_set_cvterm, get_set_cvtermprop
from chado.lib.cvterm import get_set_cvterm_dbxref, process_cvterm_xref
from chado.lib.cvterm import process_cvterm_go_synonym, process_cvterm_def
from chado.lib.dbxref import get_set_dbxref
from chado.lib.db import get_set_db
from chado.models import Cv, Cvterm, CvtermRelationship, Dbxref
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from multiprocessing import Lock
from obonet import read_obo
from tqdm import tqdm


class Command(BaseCommand):
    """Load Gene Ontology."""

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

    def store_type_def(self, typedef):
        """Store the type_def."""
        # Creating cvterm is_transitive to be used as type_id in cvtermprop
        dbxref_is_transitive = get_set_dbxref(db_name='internal',
                                              accession='is_transitive')

        cvterm_is_transitive = get_set_cvterm(
                cv_name='cvterm_property_type',
                cvterm_name='is_transitive',
                definition='',
                dbxref=dbxref_is_transitive,
                is_relationshiptype=0)

        # Creating cvterm is_class_level to be used as type_id in cvtermprop
        dbxref_is_class_level = get_set_dbxref(db_name='internal',
                                               accession='is_class_level')

        cvterm_is_class_level = get_set_cvterm(
                cv_name='cvterm_property_type',
                cvterm_name='is_class_level',
                definition='',
                dbxref=dbxref_is_class_level,
                is_relationshiptype=0)

        # Creating cvterm is_metadata_tag to be used as type_id in cvtermprop
        dbxref_is_metadata_tag = get_set_dbxref(
                db_name='internal',
                accession='is_metadata_tag')

        cvterm_is_metadata_tag = get_set_cvterm(
                cv_name='cvterm_property_type',
                cvterm_name='is_metadata_tag',
                definition='',
                dbxref=dbxref_is_metadata_tag,
                is_relationshiptype=0)

        # Save the typedef to the Dbxref model
        dbxref_typedef = get_set_dbxref(db_name='_global',
                                        accession=typedef['id'],
                                        description=typedef.get('def'))

        # Save the typedef to the Cvterm model
        cvterm_typedef = get_set_cvterm(cv_name='sequence',
                                        cvterm_name=typedef.get('id'),
                                        definition=typedef.get('def'),
                                        dbxref=dbxref_typedef,
                                        is_relationshiptype=1)

        # Load xref
        if typedef.get('xref_analog'):
            for xref in typedef.get('xref_analog'):
                process_cvterm_xref(cvterm_typedef, xref)

        # Load is_class_level
        if typedef.get('is_class_level') is not None:
            get_set_cvtermprop(
                    cvterm=cvterm_typedef,
                    type_id=cvterm_is_class_level.cvterm_id,
                    value=1,
                    rank=0)

        # Load is_metadata_tag
        if typedef.get('is_metadata_tag') is not None:
            get_set_cvtermprop(
                cvterm=cvterm_typedef,
                type_id=cvterm_is_metadata_tag.cvterm_id,
                value=1,
                rank=0)

        # Load is_transitive
        if typedef.get('is_transitive') is not None:
            get_set_cvtermprop(cvterm=cvterm_typedef,
                               type_id=cvterm_is_transitive.cvterm_id,
                               value=1,
                               rank=0)

    def store_term(self, n, data, lock):
        """Store the ontology terms."""
        # Retrieving cvterm comment to be used as type_id in cvtermprop
        cvterm_comment = get_cvterm(cv_name='cvterm_property_type',
                                    cvterm_name='comment')

        # Save the term to the Dbxref model
        aux_db, aux_accession = n.split(':')
        dbxref = get_set_dbxref(aux_db, aux_accession)

        # Save the term to the Cvterm model
        cvterm = get_set_cvterm(cv_name=data.get('namespace'),
                                cvterm_name=data.get('name'),
                                definition='',
                                dbxref=dbxref,
                                is_relationshiptype=0)

        # Definitions usually contain recurrent dbxrefs and get_set_dbxref
        # will sometimes break since they're running concurrently with
        # identical values. Locking this function call solved the problem.
        with lock:
            # Load definition and dbxrefs
            process_cvterm_def(cvterm, data.get('def'))

        # Load alt_ids
        if data.get('alt_id'):
            for alt_id in data.get('alt_id'):
                aux_db, aux_accession = alt_id.split(':')
                dbxref_alt_id = get_set_dbxref(aux_db, aux_accession)
                get_set_cvterm_dbxref(cvterm, dbxref_alt_id, 0)

        # Load comment
        if data.get('comment'):
            get_set_cvtermprop(cvterm=cvterm,
                               type_id=cvterm_comment.cvterm_id,
                               value=data.get('comment'),
                               rank=0)

        # Load xref
        if data.get('xref_analog'):
            for xref in data.get('xref_analog'):
                process_cvterm_xref(cvterm, xref)

        # Load synonyms
        for synonym_type in ('exact_synonym', 'related_synonym',
                             'narrow_synonym', 'broad_synonym'):
            if data.get(synonym_type):
                for synonym in data.get(synonym_type):
                    process_cvterm_go_synonym(cvterm, synonym,
                                              synonym_type)

    def store_relationship(self, u, v, type):
        """Store the relationship between ontology terms."""
        # retrieving term is_a to be used as type_id in cvterm_relationship
        cvterm_is_a = get_cvterm(cv_name='relationship',
                                 cvterm_name='is_a')

        # Get the subject cvterm
        subject_db_name, subject_dbxref_accession = u.split(':')
        subject_db = get_set_db(subject_db_name)
        subject_dbxref = Dbxref.objects.get(
            db=subject_db, accession=subject_dbxref_accession)
        subject_cvterm = Cvterm.objects.get(dbxref=subject_dbxref)

        # Get the object cvterm
        object_db_name, object_dbxref_accession = v.split(':')
        object_db = get_set_db(object_db_name)
        object_dbxref = Dbxref.objects.get(
            db=object_db, accession=object_dbxref_accession)
        object_cvterm = Cvterm.objects.get(dbxref=object_dbxref)

        # Get the relationship type
        if type == 'is_a':
            type_cvterm = cvterm_is_a
        else:
            type_db = get_set_db('_global')
            type_dbxref = Dbxref.objects.get(db=type_db,
                                             accession=type)
            type_cvterm = Cvterm.objects.get(dbxref=type_dbxref)

        # Save the relationship to the CvtermRelationship model
        cvrel = CvtermRelationship.objects.create(
            type_id=type_cvterm.cvterm_id,
            subject_id=subject_cvterm.cvterm_id,
            object_id=object_cvterm.cvterm_id)
        cvrel.save()

    def handle(self, *args, **options):
        """Execute the main function."""
        # Load the ontology file
        with open(options['go']) as obo_file:
            G = read_obo(obo_file)

        cv_definition = G.graph['date']

        if options.get('verbosity') > 0:
            self.stdout.write('Preprocessing')

        ontologies = [
                'biological_process',
                'molecular_function',
                'cellular_component',
                'external']

        # Check if the ontologies are already loaded
        for ontology in ontologies:

            try:
                cv = Cv.objects.get(name=ontology)
                if cv is not None:
                    if options.get('verbosity') > 0:
                        raise IntegrityError(
                                self.style.ERROR(
                                    'cv: cannot load {} {} '
                                    '(already registered)'.format(
                                        ontology, cv_definition)))
            except ObjectDoesNotExist:

                # Save ontology to the Cv model
                cv = Cv.objects.create(name=ontology,
                                       definition=cv_definition)
                cv.save()

        # Creating cvterm is_anti_symmetric to be used as type_id in cvtermprop
        dbxref_exact = get_set_dbxref(db_name='internal',
                                      accession='exact')

        get_set_cvterm(cv_name='synonym_type',
                       cvterm_name='exact',
                       definition='',
                       dbxref=dbxref_exact,
                       is_relationshiptype=0)

        # Load typedefs as Dbxrefs and Cvterm
        if options.get('verbosity') > 0:
            self.stdout.write(
                'Loading typedefs ({} threads)'.format(options.get('cpu')))

        pool = ThreadPoolExecutor(max_workers=options.get('cpu'))
        tasks = list()
        for typedef in G.graph['typedefs']:
            tasks.append(pool.submit(self.store_type_def, typedef))
        for task in as_completed(tasks):
            if task.result():
                raise(task.result())

        # Load the cvterms
        if options.get('verbosity') > 0:
            self.stdout.write(
                'Loading terms ({} threads)'.format(options.get('cpu')))

        # Creating cvterm comment to be used as type_id in cvtermprop
        dbxref_comment = get_set_dbxref(db_name='internal',
                                        accession='comment')

        get_set_cvterm(cv_name='cvterm_property_type',
                       cvterm_name='comment',
                       definition='',
                       dbxref=dbxref_comment,
                       is_relationshiptype=0)

        lock = Lock()
        tasks = list()
        for n, data in G.nodes(data=True):
            tasks.append(pool.submit(self.store_term, n, data, lock))
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        # Load the relationship between cvterms
        if options.get('verbosity') > 0:
            self.stdout.write(
                'Loading relationships ({} threads)'.format(
                    options.get('cpu')))

        # creating term is_a to be used as type_id in cvterm_relationship
        dbxref_is_a = get_set_dbxref(db_name='obo_rel',
                                     accession='is_a')

        get_set_cvterm(cv_name='relationship',
                       cvterm_name='is_a',
                       definition='',
                       dbxref=dbxref_is_a,
                       is_relationshiptype=1)

        tasks = list()
        for u, v, type in G.edges(keys=True):
            tasks.append(pool.submit(
                self.store_relationship, u, v, type))
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        # DONE
        if options.get('verbosity') > 0:
            self.stdout.write(self.style.SUCCESS('Done'))
