"""Load Gene Ontology."""

from chado.loaders.exceptions import ImportingError
from chado.loaders.common import process_cvterm_xref
from chado.loaders.common import process_cvterm_go_synonym, process_cvterm_def
from chado.loaders.common import Validator, Ontology
from chado.models import Cv, Cvterm, Cvtermprop, CvtermRelationship
from chado.models import CvtermDbxref, Db, Dbxref
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.exceptions import ObjectDoesNotExist
from multiprocessing import Lock
from obonet import read_obo
from tqdm import tqdm


class GeneOntologyLoader(object):
    """Load Gene Ontology."""

    def __init__(self, verbosity, stdout):
        """Initialization."""
        self.verbosity = verbosity
        self.stdout = stdout

    def store_type_def(self, ontology, typedef):
        """Store the type_def."""
        # Save the typedef to the Dbxref model
        dbxref_typedef, created = Dbxref.objects.get_or_create(
            db=ontology.db_global,
            accession=typedef['id'],
            defaults={'description': typedef.get('def'),
                      'version': ''})

        # Save the typedef to the Cvterm model
        cvterm_typedef, created = Cvterm.objects.get_or_create(
            cv=ontology.cv_sequence,
            name=typedef.get('id'),
            is_obsolete=0,
            dbxref=dbxref_typedef,
            defaults={'definition': typedef.get('def'),
                      'is_relationshiptype': 1})

        # Load xref
        if typedef.get('xref_analog'):
            for xref in typedef.get('xref_analog'):
                process_cvterm_xref(cvterm_typedef, xref)

        # Load is_class_level
        if typedef.get('is_class_level') is not None:
            Cvtermprop.objects.get_or_create(
                    cvterm=cvterm_typedef,
                    type_id=ontology.cvterm_is_class_level.cvterm_id,
                    value=1,
                    rank=0)

        # Load is_metadata_tag
        if typedef.get('is_metadata_tag') is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=ontology.cvterm_is_metadata_tag.cvterm_id,
                value=1,
                rank=0)

        # Load is_transitive
        if typedef.get('is_transitive') is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=ontology.cvterm_is_transitive.cvterm_id,
                value=1,
                rank=0)

    def store_term(self, ontology, n, data, lock):
        """Store the ontology terms."""
        # Save the term to the Dbxref model
        aux_db, aux_accession = n.split(':')
        db, created = Db.objects.get_or_create(name=aux_db)
        dbxref, created = Dbxref.objects.get_or_create(
            db=db, accession=aux_accession)

        # Save the term to the Cvterm model
        cv, created = Cv.objects.get_or_create(name=data.get('namespace'))
        cvterm, created = Cvterm.objects.get_or_create(
            cv=cv,
            name=data.get('name'),
            definition='',
            dbxref=dbxref,
            is_obsolete=0,
            is_relationshiptype=0)

        # Definitions usually contain recurrent dbxrefs
        # will sometimes break since they're running concurrently with
        # identical values. Locking this function call solved the problem.
        with lock:
            # Load definition and dbxrefs
            process_cvterm_def(cvterm, data.get('def'))

        # Load alt_ids
        if data.get('alt_id'):
            for alt_id in data.get('alt_id'):
                aux_db, aux_accession = alt_id.split(':')
                db_alt_id, created = Db.objects.get_or_create(name=aux_db)
                dbxref_alt_id, created = Dbxref.objects.get_or_create(
                    db=db_alt_id, accession=aux_accession)
                CvtermDbxref.objects.get_or_create(cvterm=cvterm,
                                                   dbxref=dbxref_alt_id,
                                                   is_for_definition=1)

        # Load comment
        if data.get('comment'):
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm,
                type_id=ontology.cvterm_comment.cvterm_id,
                value=data.get('comment'),
                rank=0)

        # Load xref
        if data.get('xref_analog'):
            for xref in data.get('xref_analog'):
                process_cvterm_xref(cvterm, xref, 1)

        # Load synonyms
        for synonym_type in ('exact_synonym', 'related_synonym',
                             'narrow_synonym', 'broad_synonym'):
            if data.get(synonym_type):
                for synonym in data.get(synonym_type):
                    process_cvterm_go_synonym(cvterm, synonym,
                                              synonym_type)

    def store_relationship(self, ontology, u, v, type):
        """Store the relationship between ontology terms."""
        # Get the subject cvterm
        subject_db_name, subject_dbxref_accession = u.split(':')
        subject_db, created = Db.objects.get_or_create(name=subject_db_name)
        subject_dbxref = Dbxref.objects.get(
            db=subject_db, accession=subject_dbxref_accession)
        subject_cvterm = Cvterm.objects.get(dbxref=subject_dbxref)

        # Get the object cvterm
        object_db_name, object_dbxref_accession = v.split(':')
        object_db, created = Db.objects.get_or_create(name=object_db_name)
        object_dbxref = Dbxref.objects.get(
            db=object_db, accession=object_dbxref_accession)
        object_cvterm = Cvterm.objects.get(dbxref=object_dbxref)

        # Get the relationship type
        if type == 'is_a':
            type_cvterm = ontology.cvterm_is_a
        else:
            type_dbxref = Dbxref.objects.get(db=ontology.db_global,
                                             accession=type)
            type_cvterm = Cvterm.objects.get(dbxref=type_dbxref)

        # Save the relationship to the CvtermRelationship model
        cvrel = CvtermRelationship.objects.create(
            type_id=type_cvterm.cvterm_id,
            subject_id=subject_cvterm.cvterm_id,
            object_id=object_cvterm.cvterm_id)
        cvrel.save()

    def handle(self, file, cpu=1):
        """Execute the main function."""
        Validator().validate(file)

        # Load the ontology file
        with open(file) as obo_file:
            G = read_obo(obo_file)

        cv_definition = G.graph['date']

        if self.verbosity > 0:
            self.stdout.write('Preprocessing')

        ontologies = [
                'biological_process',
                'molecular_function',
                'cellular_component']

        # Check if the ontologies are already loaded
        for ontology in ontologies:

            try:
                cv = Cv.objects.get(name=ontology)
                if cv is not None:
                    raise ImportingError(
                        'Cv -> cannot load {} {} (already registered)'.format(
                            ontology, cv_definition))

            except ObjectDoesNotExist:
                cv = Cv.objects.create(name=ontology,
                                       definition=cv_definition)
                cv.save()

        # Instantiating Ontology in order to have access to secondary cv, db,
        # cvterm, and dbxref, even though the main cv will not be used.
        ontology = Ontology('external', cv_definition)

        # Load typedefs as Dbxrefs and Cvterm
        if self.verbosity > 0:
            self.stdout.write(
                'Loading typedefs ({} threads)'.format(cpu))

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for typedef in G.graph['typedefs']:
            tasks.append(pool.submit(self.store_type_def, ontology, typedef))
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
            tasks.append(pool.submit(self.store_term, ontology, n, data, lock))
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
                self.store_relationship, ontology, u, v, type))
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
