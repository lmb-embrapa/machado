from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv,Cvprop,Cvterm,CvtermDbxref,Cvtermprop,CvtermRelationship,Cvtermsynonym,Db,Dbxref
import networkx
import obonet
from chado.lib.dbxref import *
from chado.lib.cvterm import *


class Command(BaseCommand):
    help = 'Load Relations Ontology'


    def add_arguments(self, parser):
        parser.add_argument("--ro", help="Relations Ontology file obo. Available at https://github.com/oborel/obo-relations", required = True, type=str)


    def handle(self, *args, **options):

        # Load the ontology file
        with open(options['ro']) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph['default-namespace'][0]
        cv_definition=G.graph['data-version']

        #pp = pprint.PrettyPrinter()
        #pp.pprint(G.graph)

        try:
            # Check if the so file is already loaded
            cv = Cv.objects.get(name=cv_name)

            if cv is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s %s (already registered)' % (cv_name,cv_definition)))

        except ObjectDoesNotExist:

            self.stdout.write('Preprocessing')

            # Save the name and definition to the Cv model
            cv = Cv.objects.create(name=cv_name,
                                   definition=cv_definition)
            cv.save()
            #self.stdout.write('Cv: %s %s registered' % (name,definition))

            # Creating cv cvterm_property_type
            cv_property_type = get_set_cv('cvterm_property_type','')

            # Creating cvterm is_anti_symmetric to be used as type_id in cvtermprop
            dbxref_is_anti_symmetric = get_set_dbxref('internal','is_anti_symmetric','')
            cvterm_is_anti_symmetric = get_set_cvterm(cv_property_type,'is_anti_symmetric','',dbxref_is_anti_symmetric,0)

            # Creating cvterm is_transitive to be used as type_id in cvtermprop
            dbxref_is_transitive = get_set_dbxref('internal','is_transitive','')
            cvterm_is_transitive = get_set_cvterm(cv_property_type,'is_transitive','',dbxref_is_transitive,0)

            # Creating cvterm is_reflexive to be used as type_id in cvtermprop
            dbxref_is_reflexive = get_set_dbxref('internal','is_reflexive','')
            cvterm_is_reflexive = get_set_cvterm(cv_property_type,'is_reflexive','',dbxref_is_reflexive,0)

            # Creating cvterm comment to be used as type_id in cvtermprop
            dbxref_comment = get_set_dbxref('internal','comment','')
            cvterm_comment = get_set_cvterm(cv_property_type,'comment','',dbxref_comment,0)


            # Creating cv synonym_type
            cv_synonym_type = get_set_cv('synonym_type','')

            # Creating cvterm is_anti_symmetric to be used as type_id in cvtermprop
            dbxref_exact = get_set_dbxref('internal','exact','')
            cvterm_exact = get_set_cvterm(cv_property_type,'exact','',dbxref_exact,0)



            self.stdout.write('Loading typedefs')

            for data in G.graph['typedefs']:

                # Save the term to the Dbxref model
                aux_db,aux_accession = data.get('id').split(':')
                dbxref = get_set_dbxref(aux_db,aux_accession,'')

                # Save the term to the Cvterm model
                cvterm = get_set_cvterm(cv,data.get('name'),'',dbxref,1)

                # Load definition and dbxrefs
                definition = process_cvterm_def(cvterm,data.get('def'))

                # Load is_anti_symmetric
                if data.get('is_anti_symmetric') is not None:
                    get_set_cvtermprop(cvterm=cvterm,
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
                        aux_db,aux_accession = alt_id.split(':')
                        dbxref_alt_id = get_set_dbxref(aux_db,aux_accession,'')
                        get_set_cvterm_dbxref(cvterm,dbxref_alt_id,0)

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
                        process_cvterm_xref(cvterm,xref)

                # Load synonyms
                if data.get('synonym'):
                    for synonym in data.get('synonym'):
                        process_cvterm_synonym(cvterm,synonym)

        self.stdout.write(self.style.SUCCESS('Done'))
