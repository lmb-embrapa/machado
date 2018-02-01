"""Load relations ontology."""
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv, Cvterm, Cvtermprop, CvtermDbxref, Db, Dbxref
import obonet
from chado.lib.cvterm import process_cvterm_xref
from chado.lib.cvterm import process_cvterm_def, process_cvterm_go_synonym
from tqdm import tqdm


class Command(BaseCommand):
    """Load relations ontology."""

    help = 'Load Relations Ontology'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--ro", help="Relations Ontology file obo. "
                            "Available at https://github.com/oborel/"
                            "obo-relations", required=True, type=str)
        parser.add_argument("--debug", help="debug", action='store_true')
        parser.add_argument("--silent", help="silent", action='store_true')

    def handle(self, *args, **options):
        """Execute the main function."""
        # Verbosity
        verbosity = 1
        if(options['debug']):
            verbosity = 2

        # Load the ontology file
        with open(options['ro']) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = 'relationship'

        try:
            # Check if the so file is already loaded
            cv = Cv.objects.get(name=cv_name)

            if cv is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s '
                                                   '(already registered)'
                                                   % (cv_name)))

        except ObjectDoesNotExist:

            if verbosity > 0:
                self.stdout.write('Preprocessing')

            # Save the name and definition to the Cv model
            cv = Cv.objects.create(name=cv_name)
            cv.save()

            # Creating db internal to be used for creating dbxref objects
            db_internal, created = Db.objects.get_or_create(
                name='internal')

            # Creating dbxref is_anti_symmetric to be used for creating cvterms
            dbxref_is_anti_symmetric, created = Dbxref.objects.get_or_create(
                db=db_internal, accession='is_anti_symmetric')

            # Creating cv cvterm_property_type to be used for creating cvterms
            cv_cvterm_property_type, created = Cv.objects.get_or_create(
                name='cvterm_property_type')

            # Creating cvterm is_anti_symmetric to be used as type_id in
            # cvtermprop
            cvterm_is_anti_symmetric, created = Cvterm.objects.get_or_create(
                    cv=cv_cvterm_property_type,
                    name='is_anti_symmetric',
                    definition='',
                    dbxref=dbxref_is_anti_symmetric,
                    is_obsolete=0,
                    is_relationshiptype=0)

            # Creating cvterm is_transitive to be used as type_id in
            # cvtermprop
            dbxref_is_transitive, created = Dbxref.objects.get_or_create(
                db=db_internal, accession='is_transitive')
            cvterm_is_transitive, created = Cvterm.objects.get_or_create(
                    cv=cv_cvterm_property_type,
                    name='is_transitive',
                    definition='',
                    dbxref=dbxref_is_transitive,
                    is_obsolete=0,
                    is_relationshiptype=0)

            # Creating cvterm is_reflexive to be used as type_id in cvtermprop
            dbxref_is_reflexive, created = Dbxref.objects.get_or_create(
                db=db_internal, accession='is_reflexive')
            cvterm_is_reflexive, created = Cvterm.objects.get_or_create(
                    cv=cv_cvterm_property_type,
                    name='is_reflexive',
                    definition='',
                    dbxref=dbxref_is_reflexive,
                    is_obsolete=0,
                    is_relationshiptype=0)

            # Creating cvterm comment to be used as type_id in cvtermprop
            dbxref_comment, created = Dbxref.objects.get_or_create(
                db=db_internal, accession='comment')
            cvterm_comment, created = Cvterm.objects.get_or_create(
                cv=cv_cvterm_property_type,
                name='comment',
                definition='',
                dbxref=dbxref_comment,
                is_obsolete=0,
                is_relationshiptype=0)

            # Creating cvterm is_anti_symmetric to be used as type_id in
            # cvtermprop
            dbxref_exact, created = Dbxref.objects.get_or_create(
                db=db_internal, accession='exact')
            cv_synonym_type, created = Cv.objects.get_or_create(
                name='synonym_type')
            Cvterm.objects.get_or_create(cv=cv_synonym_type,
                                         name='exact',
                                         definition='',
                                         dbxref=dbxref_exact,
                                         is_obsolete=0,
                                         is_relationshiptype=0)

            if verbosity > 0:
                self.stdout.write('Loading typedefs')

            for data in tqdm(G.graph['typedefs']):

                if verbosity > 1:
                    self.stdout.write('  typedef id: %s' % data.get('id'))
                # Save the term to the Dbxref model
                try:
                    aux_db, aux_accession = data.get('id').split(':')
                    db, created = Db.objects.get_or_create(name=aux_db)
                    dbxref, created = Dbxref.objects.get_or_create(
                        db=db, accession=aux_accession)
                except ValueError:
                    continue

                # Save the term to the Cvterm model
                cv, created = Cv.objects.get_or_create(name=cv.name)
                cvterm, created = Cvterm.objects.get_or_create(
                    cv=cv,
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
                        type_id=cvterm_is_anti_symmetric.cvterm_id,
                        value=1,
                        rank=0)

                # Load is_reflexive
                if data.get('is_reflexive') is not None:
                    Cvtermprop.objects.get_or_create(
                        cvterm=cvterm,
                        type_id=cvterm_is_reflexive.cvterm_id,
                        value=1,
                        rank=0)

                # Load is_transitive
                if data.get('is_transitive') is not None:
                    Cvtermprop.objects.get_or_create(
                        cvterm=cvterm,
                        type_id=cvterm_is_transitive.cvterm_id,
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
                            type_id=cvterm_comment.cvterm_id,
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

        self.stdout.write(self.style.SUCCESS('Done'))
