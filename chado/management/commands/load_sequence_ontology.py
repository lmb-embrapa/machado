from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv, Cvterm, CvtermRelationship, Dbxref
import obonet
from chado.lib.dbxref import get_set_dbxref
from chado.lib.db import get_set_db
from chado.lib.cvterm import get_set_cvterm, get_set_cvtermprop
from chado.lib.cvterm import get_set_cvterm_dbxref, process_cvterm_xref
from chado.lib.cvterm import process_cvterm_so_synonym, process_cvterm_def


class Command(BaseCommand):
    help = 'Load Sequence Ontology'

    def add_arguments(self, parser):
        parser.add_argument("--so", help="Sequence Ontology file obo."
                            "Available at https://github.com/"
                            "The-Sequence-Ontology/SO-Ontologies",
                            required=True, type=str)

    def handle(self, *args, **options):

        # Load the ontology file
        with open(options['so']) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph['default-namespace'][0]
        cv_definition = G.graph['data-version']

        try:
            # Check if the so file is already loaded
            cv = Cv.objects.get(name=cv_name)

            if cv is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s %s'
                                                   '(already registered)'
                                                   % (cv_name, cv_definition)))

        except ObjectDoesNotExist:

            self.stdout.write('Preprocessing')

            # Save the name and definition to the Cv model
            cv = Cv.objects.create(name=cv_name,
                                   definition=cv_definition)
            cv.save()

            # Creating cvterm is_symmetric to be used as type_id in cvtermprop
            dbxref_is_symmetric = get_set_dbxref('internal',
                                                 'is_symmetric')
            cvterm_is_symmetric = get_set_cvterm('cvterm_property_type',
                                                 'is_symmetric', '',
                                                 dbxref_is_symmetric, 0)

            # Creating cvterm is_transitive to be used as type_id in cvtermprop
            dbxref_is_transitive = get_set_dbxref('internal',
                                                  'is_transitive')
            cvterm_is_transitive = get_set_cvterm('cvterm_property_type',
                                                  'is_transitive',
                                                  '',
                                                  dbxref_is_transitive,
                                                  0)

            self.stdout.write('Loading typedefs')

            # Load typedefs as Dbxrefs and Cvterm
            for typedef in G.graph['typedefs']:
                dbxref_typedef = get_set_dbxref(db_name='_global',
                                                accession=typedef['id'],
                                                description=typedef.get('def'))
                cvterm_typedef = get_set_cvterm(cv.name,
                                                typedef.get('id'),
                                                typedef.get('def'),
                                                dbxref_typedef,
                                                1)

                # Load is_symmetric
                if typedef.get('is_symmetric') is not None:
                    get_set_cvtermprop(cvterm=cvterm_typedef,
                                       type_id=cvterm_is_symmetric.cvterm_id,
                                       value=1,
                                       rank=0)
                # Load is_transitive
                if typedef.get('is_transitive') is not None:
                    get_set_cvtermprop(cvterm=cvterm_typedef,
                                       type_id=cvterm_is_transitive.cvterm_id,
                                       value=1,
                                       rank=0)

            self.stdout.write('Loading terms')

            # Creating cvterm comment to be used as type_id in cvtermprop
            dbxref_comment = get_set_dbxref('internal', 'comment')
            cvterm_comment = get_set_cvterm('cvterm_property_type',
                                            'comment',
                                            '',
                                            dbxref_comment,
                                            0)

            for n, data in G.nodes(data=True):

                # Save the term to the Dbxref model
                aux_db, aux_accession = n.split(':')
                dbxref = get_set_dbxref(aux_db, aux_accession)

                # Save the term to the Cvterm model
                cvterm = get_set_cvterm(cv.name,
                                        data.get('name'),
                                        '',
                                        dbxref,
                                        0)

                # Load definition and dbxrefs
                process_cvterm_def(cvterm, data.get('def'))

                # Load alt_ids
                if data.get('alt_id'):
                    for alt_id in data.get('alt_id'):
                        aux_db, aux_accession = alt_id.split(':')
                        dbxref_alt_id = get_set_dbxref(aux_db,
                                                       aux_accession)
                        get_set_cvterm_dbxref(cvterm,
                                              dbxref_alt_id,
                                              0)

                # Load comment
                if data.get('comment'):
                    get_set_cvtermprop(cvterm=cvterm,
                                       type_id=cvterm_comment.cvterm_id,
                                       value=data.get('comment'),
                                       rank=0)

                # Load xref
                if data.get('xref'):
                    for xref in data.get('xref'):
                        process_cvterm_xref(cvterm, xref)

                # Load synonyms
                if data.get('synonym'):
                    for synonym in data.get('synonym'):
                        process_cvterm_so_synonym(cvterm, synonym)

            self.stdout.write('Loading relationships')

            # Creating term is_a to be used as type_id in cvterm_relationship
            dbxref_is_a = get_set_dbxref('OBO_REL', 'is_a')
            cvterm_is_a = get_set_cvterm('relationship',
                                         'is_a',
                                         '',
                                         dbxref_is_a,
                                         1)

            for u, v, type in G.edges(keys=True):

                # Get the subject cvterm
                subject_db_name, subject_dbxref_accession = u.split(':')
                subject_db = get_set_db(subject_db_name)
                subject_dbxref = Dbxref.objects.get(
                    db=subject_db,
                    accession=subject_dbxref_accession)
                subject_cvterm = Cvterm.objects.get(dbxref=subject_dbxref)

                # Get the object cvterm
                object_db_name, object_dbxref_accession = v.split(':')
                object_db = get_set_db(object_db_name)
                object_dbxref = Dbxref.objects.get(
                    db=object_db,
                    accession=object_dbxref_accession)
                object_cvterm = Cvterm.objects.get(dbxref=object_dbxref)

                if type == 'is_a':
                    type_cvterm = cvterm_is_a
                else:
                    type_db = get_set_db('_global')
                    type_dbxref = Dbxref.objects.get(db=type_db,
                                                     accession=type)
                    type_cvterm = Cvterm.objects.get(dbxref=type_dbxref)

                cvrel = CvtermRelationship.objects.create(
                    type_id=type_cvterm.cvterm_id,
                    subject_id=subject_cvterm.cvterm_id,
                    object_id=object_cvterm.cvterm_id)
                cvrel.save()

        self.stdout.write(self.style.SUCCESS('Done'))
