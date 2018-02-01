"""Load Sequence Ontology."""
from chado.loaders.exceptions import ImportingError
from chado.loaders.common import Validator
from chado.loaders.common import process_cvterm_xref, process_cvterm_def
from chado.models import Cv, Cvterm, Cvtermprop, CvtermRelationship
from chado.models import CvtermDbxref, Cvtermsynonym, Db, Dbxref
from django.core.exceptions import ObjectDoesNotExist
from tqdm import tqdm
import obonet
import re


class SequenceOntologyLoader(object):
    """Load Sequence Ontology."""

    def __init__(self, verbosity, stdout):
        """Initialization."""
        self.verbosity = verbosity
        self.stdout = stdout

    def preprocessing(self, cv_name, cv_definition):
        """Create cv and cvterms."""
        # Save the name and definition to the Cv model
        # Save the name and definition to the Cv model
        self.cv = Cv.objects.create(name=cv_name,
                                    definition=cv_definition)
        self.cv.save()

        self.db_global, created = Db.objects.get_or_create(name='_global')

        # Creating db internal to be used for creating dbxref objects
        self.db_internal, created = Db.objects.get_or_create(name='internal')

        # Creating dbxref is_symmetric to be used for creating cvterms
        dbxref_is_symmetric, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_symmetric')

        # Creating cv cvterm_property_type to be used for creating cvterms
        cv_cvterm_property_type, created = Cv.objects.get_or_create(
            name='cvterm_property_type')

        # Creating cvterm is_symmetric to be used as type_id in cvtermprop
        self.cvterm_is_symmetric, created = Cvterm.objects.get_or_create(
                cv=cv_cvterm_property_type,
                name='is_symmetric',
                definition='',
                dbxref=dbxref_is_symmetric,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating cvterm is_transitive to be used as type_id in cvtermprop
        dbxref_is_transitive, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_transitive')
        self.cvterm_is_transitive, created = Cvterm.objects.get_or_create(
                cv=cv_cvterm_property_type,
                name='is_transitive',
                definition='',
                dbxref=dbxref_is_transitive,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating cvterm comment to be used as type_id in cvtermprop
        dbxref_comment, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='comment')
        self.cvterm_comment, created = Cvterm.objects.get_or_create(
            cv=cv_cvterm_property_type,
            name='comment',
            definition='',
            dbxref=dbxref_comment,
            is_obsolete=0,
            is_relationshiptype=0)

        # Creating term is_a to be used as type_id in cvterm_relationship
        db_obo_rel, created = Db.objects.get_or_create(name='obo_rel')
        dbxref_is_a, created = Dbxref.objects.get_or_create(
            db=db_obo_rel, accession='is_a')
        cv_relationship, created = Cv.objects.get_or_create(
            name='relationship')
        self.cvterm_is_a, created = Cvterm.objects.get_or_create(
            cv=cv_relationship,
            name='is_a',
            definition='',
            dbxref=dbxref_is_a,
            is_obsolete=0,
            is_relationshiptype=1)

    def process_cvterm_so_synonym(self, cvterm, synonym):
        """Process cvterm_so_synonym.

        Definition format:
        "text" cvterm []

        Definition format example:
        "stop codon gained" EXACT []

        Attention:
        There are several cases that don't follow this format.
        Those are being ignored for now.
        """
        pattern = re.compile(r'^"(.+)" (\w+) \[\]$')
        matches = pattern.findall(synonym)

        if len(matches) != 1 or len(matches[0]) != 2:
            return

        synonym_text, synonym_type = matches[0]

        # Handling the synonym_type
        db_type, created = Db.objects.get_or_create(name='internal')
        dbxref_type, created = Dbxref.objects.get_or_create(
            db=db_type, accession=synonym_type.lower())
        cv_synonym_type, created = Cv.objects.get_or_create(
            name='synonym_type')
        cvterm_type, created = Cvterm.objects.get_or_create(
            cv=cv_synonym_type,
            name=synonym_type.lower(),
            definition='',
            dbxref=dbxref_type,
            is_obsolete=0,
            is_relationshiptype=0)

        # Storing the synonym
        cvtermsynonym = Cvtermsynonym.objects.create(
            cvterm=cvterm, synonym=synonym_text, type_id=cvterm_type.cvterm_id)
        cvtermsynonym.save()
        return

    def store_type_def(self, typedef):
        """Store the type_def."""
        dbxref_typedef, created = Dbxref.objects.get_or_create(
            db=self.db_global,
            accession=typedef['id'],
            description=typedef.get('def'))
        cv_typedef, created = Cv.objects.get_or_create(name=self.cv.name)
        cvterm_typedef, created = Cvterm.objects.get_or_create(
            cv=cv_typedef,
            name=typedef.get('id'),
            definition=typedef.get('def'),
            dbxref=dbxref_typedef,
            is_obsolete=0,
            is_relationshiptype=1)

        # Load is_symmetric
        if typedef.get('is_symmetric') is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=self.cvterm_is_symmetric.cvterm_id,
                value=1,
                rank=0)
        # Load is_transitive
        if typedef.get('is_transitive') is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=self.cvterm_is_transitive.cvterm_id,
                value=1,
                rank=0)

    def store_term(self, n, data):
        """Store the ontology terms."""
        # Save the term to the Dbxref model
        aux_db, aux_accession = n.split(':')

        db, created = Db.objects.get_or_create(name=aux_db)
        dbxref, created = Dbxref.objects.get_or_create(
            db=db, accession=aux_accession)

        if self.verbosity > 1:
            self.stdout.write('{} {}'.format(n, data))

        # Save the term to the Cvterm model
        cvterm, created = Cvterm.objects.get_or_create(
            cv=self.cv,
            name=data.get('name'),
            definition='',
            dbxref=dbxref,
            is_obsolete=0,
            is_relationshiptype=0)

        # Load definition and dbxrefs
        process_cvterm_def(cvterm, data.get('def'))

        # Load alt_ids
        if data.get('alt_id'):
            for alt_id in data.get('alt_id'):
                aux_db, aux_accession = alt_id.split(':')

                db_alt_id, created = Db.objects.get_or_create(
                    name=aux_db)
                dbxref_alt_id, created = Dbxref.objects.get_or_create(
                    db=db_alt_id, accession=aux_accession)
                CvtermDbxref.objects.get_or_create(
                    cvterm=cvterm,
                    dbxref=dbxref_alt_id,
                    is_for_definition=0)

        # Load comment
        if data.get('comment'):
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm,
                type_id=self.cvterm_comment.cvterm_id,
                value=data.get('comment'),
                rank=0)

        # Load xref
        if data.get('xref'):
            for xref in data.get('xref'):
                process_cvterm_xref(cvterm, xref, 1)

        # Load synonyms
        if data.get('synonym'):
            for synonym in data.get('synonym'):
                self.process_cvterm_so_synonym(cvterm, synonym)

    def store_relationship(self, u, v, type):
        """Store the relationship between ontology terms."""
        # Get the subject cvterm
        subject_db_name, subject_dbxref_accession = u.split(':')
        subject_db, created = Db.objects.get_or_create(
            name=subject_db_name)
        subject_dbxref = Dbxref.objects.get(
            db=subject_db,
            accession=subject_dbxref_accession)
        subject_cvterm = Cvterm.objects.get(dbxref=subject_dbxref)

        # Get the object cvterm
        object_db_name, object_dbxref_accession = v.split(':')
        object_db, created = Db.objects.get_or_create(
            name=object_db_name)
        object_dbxref = Dbxref.objects.get(
            db=object_db,
            accession=object_dbxref_accession)
        object_cvterm = Cvterm.objects.get(dbxref=object_dbxref)

        if type == 'is_a':
            type_cvterm = self.cvterm_is_a
        else:
            type_db, created = Db.objects.get_or_create(name='_global')
            type_dbxref = Dbxref.objects.get(db=type_db,
                                             accession=type)
            type_cvterm = Cvterm.objects.get(dbxref=type_dbxref)

        cvrel = CvtermRelationship.objects.create(
            type_id=type_cvterm.cvterm_id,
            subject_id=subject_cvterm.cvterm_id,
            object_id=object_cvterm.cvterm_id)
        cvrel.save()

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

        try:
            # Check if the so file is already loaded
            cv = Cv.objects.get(name=cv_name)

            if cv is not None:
                raise ImportingError(
                    'Cv -> cannot load {} {} (already registered)'.format(
                        cv_name, cv_definition))

        except ObjectDoesNotExist:
            self.preprocessing(cv_name, cv_definition)

        if self.verbosity > 0:
            self.stdout.write('Loading typedefs')

        # Load typedefs as Dbxrefs and Cvterm
        for typedef in tqdm(G.graph['typedefs']):
            self.store_type_def(typedef)

        if self.verbosity > 0:
            self.stdout.write('Loading terms')

        for n, data in tqdm(G.nodes(data=True)):
            self.store_term(n, data)

        if self.verbosity > 0:
            self.stdout.write('Loading relationships')

        for u, v, type in tqdm(G.edges(keys=True)):
            self.store_relationship(u, v, type)
