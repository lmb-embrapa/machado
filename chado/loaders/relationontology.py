"""Load relations ontology."""

from chado.models import Cvterm, Cvtermprop, CvtermDbxref, Db, Dbxref
import obonet
from chado.loaders.common import Validator, Ontology
from chado.loaders.common import process_cvterm_xref
from chado.loaders.common import process_cvterm_def, process_cvterm_go_synonym
from tqdm import tqdm


class RelationOntologyLoader(object):
    """Load relations ontology."""

    def __init__(self, verbosity, stdout):
        """Initialization."""
        self.verbosity = verbosity
        self.stdout = stdout

    def store_type_def(self, ontology, data):
        """Store the type_def."""
        if self.verbosity > 1:
            self.stdout.write('  typedef id: {}'.format(
                data.get('id')))

        # Save the term to the Dbxref model
        if ':' in data.get('id'):
            aux_db, aux_accession = data.get('id').split(':')
        else:
            aux_db = '_global'
            aux_accession = data.get('id')
        db, created = Db.objects.get_or_create(name=aux_db)
        dbxref, created = Dbxref.objects.get_or_create(
            db=db, accession=aux_accession)

        # Save the term to the Cvterm model
        cvterm, created = Cvterm.objects.get_or_create(
            cv=ontology.cv,
            name=data.get('name'),
            definition='',
            dbxref=dbxref,
            is_obsolete=0,
            is_relationshiptype=1)

        # Load definition and dbxrefs
        process_cvterm_def(cvterm, data.get('def'))

        # Load is_anti_symmetric
        if data.get('is_anti_symmetric') is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm,
                type_id=ontology.cvterm_is_anti_symmetric.cvterm_id,
                value=1,
                rank=0)

        # Load is_reflexive
        if data.get('is_reflexive') is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm,
                type_id=ontology.cvterm_is_reflexive.cvterm_id,
                value=1,
                rank=0)

        # Load is_transitive
        if data.get('is_transitive') is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm,
                type_id=ontology.cvterm_is_transitive.cvterm_id,
                value=1,
                rank=0)

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
            for comment in data.get('comment'):
                Cvtermprop.objects.get_or_create(
                    cvterm=cvterm,
                    type_id=ontology.cvterm_comment.cvterm_id,
                    value=comment,
                    rank=0)

        # Load xref
        if data.get('xref'):
            for xref in data.get('xref'):
                process_cvterm_xref(cvterm, xref, 1)

        # Load synonyms
        for synonym_type in ('exact_synonym', 'related_synonym',
                             'narrow_synonym', 'broad_synonym'):
            if data.get(synonym_type):
                for synonym in data.get(synonym_type):
                    process_cvterm_go_synonym(cvterm,
                                              synonym,
                                              synonym_type)

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
            self.store_type_def(ontology, data)
