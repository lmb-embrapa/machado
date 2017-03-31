from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv,Cvprop,Cvterm,CvtermDbxref,Cvtermprop,CvtermRelationship,Cvtermsynonym,Db,Dbxref
import networkx
import obonet
from chado.lib.dbxref import *
from chado.lib.cvterm import *


class Command(BaseCommand):
    help = 'Load Gene Ontology'


    def add_arguments(self, parser):
        parser.add_argument("--go", help="Gene Ontology file obo. Available at http://www.geneontology.org/ontology/gene_ontology.obo", required = True, type=str)


    def handle(self, *args, **options):

        # Load the ontology file
        with open(options['go']) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_definition=G.graph['date']

        #pp = pprint.PrettyPrinter()
        #pp.pprint(G.graph)

        try:
            # Check if the so file is already loaded
            cv_bp = Cv.objects.get(name='biological_process')
            if cv_bp is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s %s (already registered)' % ('biological_process',cv_definition)))

            cv_mf = Cv.objects.get(name='molecular_function')
            if cv_mf is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s %s (already registered)' % ('molecular_function',cv_definition)))

            cv_cc = Cv.objects.get(name='cellular_component')
            if cv_cc is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s %s (already registered)' % ('cellular_component',cv_definition)))

            cv_ex = Cv.objects.get(name='external')
            if cv_ex is not None:
                self.stdout.write(self.style.ERROR('cv: cannot load %s %s (already registered)' % ('external',cv_definition)))

        except ObjectDoesNotExist:

            self.stdout.write('Preprocessing')

            # Save biological_process, molecular_function, and cellular_component to the Cv model
            cv_bp = Cv.objects.create(name='biological_process',definition=cv_definition)
            cv_bp.save()
            cv_mf = Cv.objects.create(name='molecular_function',definition=cv_definition)
            cv_mf.save()
            cv_cc = Cv.objects.create(name='cellular_component',definition=cv_definition)
            cv_cc.save()
            cv_ex = Cv.objects.create(name='external',definition=cv_definition)
            cv_ex.save()


            # creating term is_a to be used as type_id in cvterm_relationship
            cv_relationship = get_set_cv('relationship','')
            dbxref_is_a = get_set_dbxref('obo_rel','is_a','')
            cvterm_is_a = get_set_cvterm(cv_relationship,'is_a','',dbxref_is_a,1)

            # creating term regulates to be used as type_id in cvterm_relationship
            dbxref_regulates = get_set_dbxref('_global','regulates','')
            cvterm_regulates = get_set_cvterm(cv_ex,'regulates','',dbxref_regulates,1)


            # Creating cv cvterm_property_type
            cv_property_type = get_set_cv('cvterm_property_type','')

            # Creating cv synonym_property_type
            cv_synonym_type = get_set_cv('synonym_type','')


            # Creating cvterm is_transitive to be used as type_id in cvtermprop
            dbxref_is_transitive = get_set_dbxref('internal','is_transitive','')
            cvterm_is_transitive = get_set_cvterm(cv_property_type,'is_transitive','',dbxref_is_transitive,0)

            # Creating cvterm is_class_level to be used as type_id in cvtermprop
            dbxref_is_class_level = get_set_dbxref('internal','is_class_level','')
            cvterm_is_class_level = get_set_cvterm(cv_property_type,'is_class_level','',dbxref_is_class_level,0)

            # Creating cvterm is_metadata_tag to be used as type_id in cvtermprop
            dbxref_is_metadata_tag = get_set_dbxref('internal','is_metadata_tag','')
            cvterm_is_metadata_tag = get_set_cvterm(cv_property_type,'is_metadata_tag','',dbxref_is_metadata_tag,0)

            # Creating cvterm comment to be used as type_id in cvtermprop
            dbxref_comment = get_set_dbxref('internal','comment','')
            cvterm_comment = get_set_cvterm(cv_property_type,'comment','',dbxref_comment,0)

            # Creating cvterm is_anti_symmetric to be used as type_id in cvtermprop
            dbxref_exact = get_set_dbxref('internal','exact','')
            cvterm_exact = get_set_cvterm(cv_synonym_type,'exact','',dbxref_exact,0)


            self.stdout.write('Loading typedefs')

            # Load typedefs as Dbxrefs and Cvterm
            for typedef in G.graph['typedefs']:
                dbxref_typedef = get_set_dbxref('_global',typedef['id'],typedef.get('def'))
                cvterm_typedef = get_set_cvterm(cv_ex,typedef.get('id'),typedef.get('def'),dbxref_typedef,1)

                # Load xref
                if typedef.get('xref_analog'):
                    for xref in typedef.get('xref_analog'):
                        process_cvterm_xref(cvterm_typedef,xref)

                # Load is_class_level
                if typedef.get('is_class_level') is not None:
                    get_set_cvtermprop(cvterm=cvterm_typedef,
                                       type_id=cvterm_is_class_level.cvterm_id,
                                       value=1,
                                       rank=0)

                # Load is_metadata_tag
                if typedef.get('is_metadata_tag') is not None:
                    get_set_cvtermprop(cvterm=cvterm_typedef,
                                       type_id=cvterm_is_metadata_tag.cvterm_id,
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
            dbxref_comment = get_set_dbxref('internal','comment','')
            cvterm_comment = get_set_cvterm(cv_property_type,'comment','',dbxref_comment,0)

            for n,data in G.nodes(data=True):

                # Save the term to the Dbxref model
                aux_db,aux_accession = n.split(':')
                dbxref = get_set_dbxref(aux_db,aux_accession,'')

                # Regrieve the appropriate cv
                cv = Cv.objects.get(name=data.get('namespace'))

                # Save the term to the Cvterm model
                cvterm = get_set_cvterm(cv,data.get('name'),'',dbxref,0)

                # Load definition and dbxrefs
                definition = process_cvterm_def(cvterm,data.get('def'))

                # Load alt_ids
                if data.get('alt_id'):
                    for alt_id in data.get('alt_id'):
                        aux_db,aux_accession = alt_id.split(':')
                        dbxref_alt_id = get_set_dbxref(aux_db,aux_accession,'')
                        get_set_cvterm_dbxref(cvterm,dbxref_alt_id,0)

                # Load comment
                if data.get('comment'):
                    get_set_cvtermprop(cvterm=cvterm,
                                       type_id=cvterm_comment.cvterm_id,
                                       value=data.get('comment'),
                                       rank=0)

                # Load xref
                if data.get('xref_analog'):
                    for xref in data.get('xref_analog'):
                        process_cvterm_xref(cvterm,xref)

                # Load synonyms
                for synonym_type in ('exact_synonym','related_synonym','narrow_synonym','broad_synonym'):
                    if data.get(synonym_type):
                        for synonym in data.get(synonym_type):
                            process_cvterm_go_synonym(cvterm,synonym,synonym_type)


            self.stdout.write('Loading relationships')

            # Creating term is_a to be used as type_id in cvterm_relationship
            cv_relationship = get_set_cv('cvterm_relationship','')
            dbxref_is_a = get_set_dbxref('OBO_REL','is_a','')
            cvterm_is_a = get_set_cvterm(cv_relationship,'is_a','',dbxref_is_a,1)


            for u,v,type in G.edges(keys=True):

                # Get the subject cvterm
                subject_db_name,subject_dbxref_accession = u.split(':')
                subject_dbxref = Dbxref.objects.get(accession=subject_dbxref_accession)
                subject_cvterm = Cvterm.objects.get(dbxref=subject_dbxref)

                # Get the object cvterm
                object_db_name,object_dbxref_accession = v.split(':')
                object_dbxref = Dbxref.objects.get(accession=object_dbxref_accession)
                object_cvterm = Cvterm.objects.get(dbxref=object_dbxref)

                if type == 'is_a':
                    type_cvterm = cvterm_is_a
                else:
                    type_dbxref = Dbxref.objects.get(accession=type)
                    type_cvterm = Cvterm.objects.get(dbxref=type_dbxref)

                cvrel = CvtermRelationship.objects.create(type_id=type_cvterm.cvterm_id,
                                                          subject_id=subject_cvterm.cvterm_id,
                                                          object_id=object_cvterm.cvterm_id)
                cvrel.save()

        self.stdout.write(self.style.SUCCESS('Done'))
