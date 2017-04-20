from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv
import obonet
from chado.lib.dbxref import get_set_dbxref
from chado.lib.cvterm import get_set_cvterm, get_set_cvtermprop
from chado.lib.cvterm import get_set_cvterm_dbxref, process_cvterm_xref
from chado.lib.cvterm import process_cvterm_def, process_cvterm_go_synonym


class Command(BaseCommand):
    help = 'Load Relations Ontology'

    def add_arguments(self, parser):
        parser.add_argument("--ro", help="Relations Ontology file obo. "
                            "Available at https://github.com/oborel/"
                            "obo-relations", required=True, type=str)

    def handle(self, *args, **options):

        # Load the ontology file
        with open(options['ro']) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph['default-namespace'][0]

        try:
            # Check if the so file is already loaded
            cv = Cv.objects.get(name=cv_name)

            if cv is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s '
                                                   '(already registered)'
                                                   % (cv_name)))

        except ObjectDoesNotExist:

            self.stdout.write('Preprocessing')

            # Save the name and definition to the Cv model
            cv = Cv.objects.create(name=cv_name)
            cv.save()

            # Creating cvterm is_anti_symmetric to be used as type_id in
            # cvtermprop
            dbxref_is_anti_symmetric = get_set_dbxref('internal',
                                                      'is_anti_symmetric',
                                                      '')
            cvterm_is_anti_symmetric = get_set_cvterm('cvterm_property_type',
                                                      'is_anti_symmetric', '',
                                                      dbxref_is_anti_symmetric,
                                                      0)

            # Creating cvterm is_transitive to be used as type_id in
            # cvtermprop
            dbxref_is_transitive = get_set_dbxref('internal',
                                                  'is_transitive', '')
            cvterm_is_transitive = get_set_cvterm('cvterm_property_type',
                                                  'is_transitive', '',
                                                  dbxref_is_transitive, 0)

            # Creating cvterm is_reflexive to be used as type_id in cvtermprop
            dbxref_is_reflexive = get_set_dbxref('internal',
                                                 'is_reflexive', '')
            cvterm_is_reflexive = get_set_cvterm('cvterm_property_type',
                                                 'is_reflexive', '',
                                                 dbxref_is_reflexive, 0)

            # Creating cvterm comment to be used as type_id in cvtermprop
            dbxref_comment = get_set_dbxref('internal', 'comment', '')
            cvterm_comment = get_set_cvterm('cvterm_property_type',
                                            'comment', '', dbxref_comment, 0)

            # Creating cvterm is_anti_symmetric to be used as type_id in
            # cvtermprop
            dbxref_exact = get_set_dbxref('internal', 'exact', '')
            get_set_cvterm('synonym_type', 'exact', '',
                           dbxref_exact, 0)

            self.stdout.write('Loading typedefs')

            for data in G.graph['typedefs']:

                # Save the term to the Dbxref model
                aux_db, aux_accession = data.get('id').split(':')
                dbxref = get_set_dbxref(aux_db, aux_accession, '')

                # Save the term to the Cvterm model
                cvterm = get_set_cvterm(cv.name, data.get('name'), '',
                                        dbxref, 1)

                # Load definition and dbxrefs
                process_cvterm_def(cvterm, data.get('def'))

                # Load is_anti_symmetric
                if data.get('is_anti_symmetric') is not None:
                    get_set_cvtermprop(
                        cvterm=cvterm,
                        type_id=cvterm_is_anti_symmetric.cvterm_id,
                        value=1,
                        rank=0)

                # Load is_reflexive
                if data.get('is_reflexive') is not None:
                    get_set_cvtermprop(cvterm=cvterm,
                                       type_id=cvterm_is_reflexive.cvterm_id,
                                       value=1,
                                       rank=0)

                # Load is_transitive
                if data.get('is_transitive') is not None:
                    get_set_cvtermprop(cvterm=cvterm,
                                       type_id=cvterm_is_transitive.cvterm_id,
                                       value=1,
                                       rank=0)

                # Load alt_ids
                if data.get('alt_id'):
                    for alt_id in data.get('alt_id'):
                        aux_db, aux_accession = alt_id.split(':')
                        dbxref_alt_id = get_set_dbxref(aux_db,
                                                       aux_accession,
                                                       '')
                        get_set_cvterm_dbxref(cvterm, dbxref_alt_id, 0)

                # Load comment
                if data.get('comment'):
                    for comment in data.get('comment'):
                        get_set_cvtermprop(cvterm=cvterm,
                                           type_id=cvterm_comment.cvterm_id,
                                           value=comment,
                                           rank=0)

                # Load xref
                if data.get('xref'):
                    for xref in data.get('xref'):
                        process_cvterm_xref(cvterm, xref)

                # Load synonyms
                for synonym_type in ('exact_synonym', 'related_synonym',
                                     'narrow_synonym', 'broad_synonym'):
                    if data.get(synonym_type):
                        for synonym in data.get(synonym_type):
                            process_cvterm_go_synonym(cvterm,
                                                      synonym,
                                                      synonym_type)

        self.stdout.write(self.style.SUCCESS('Done'))
