from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv,Cvprop,Cvterm,CvtermDbxref,Cvtermprop,CvtermRelationship,Cvtermsynonym,Db,Dbxref
import networkx
import obonet
import re
import pprint


class Command(BaseCommand):
    help = 'Load Relations Ontology'


    def add_arguments(self, parser):
        parser.add_argument("--ro", help="Relations Ontology file obo. Available at https://github.com/oborel/obo-relations", required = True, type=str)


    def _get_cv(self,name,definition):

        try:
            # Check if the cv is already registered
            cv = Cv.objects.get(name=name)
            return cv

        except ObjectDoesNotExist:

            # Save the name to the Db model
            cv = Cv.objects.create(name=name,definition=definition)
            cv.save()
            #self.stdout.write('Cv: %s registered' % name)
            return cv


    def _get_cvterm(self,cv,name,definition,dbxref,is_relationshiptype):

        try:
            # Check if the cvterm is already registered
            cvterm = Cvterm.objects.get(cv=cv,name=name,dbxref=dbxref)
            return cvterm

        except ObjectDoesNotExist:

            # Save the name to the Db model
            cvterm = Cvterm.objects.create(cv=cv,
                                           name=name,
                                           definition=definition,
                                           dbxref=dbxref,
                                           is_obsolete=0,
                                           is_relationshiptype=is_relationshiptype)
            cvterm.save()
            #self.stdout.write('Cvterm: %s registered' % name)
            return cvterm


    def _get_db(self,name):

        try:
            # Check if the db is already registered
            db = Db.objects.get(name=name)
            return db

        except ObjectDoesNotExist:

            # Save the name to the Db model
            db = Db.objects.create(name=name)
            db.save()
            #self.stdout.write('Db: %s registered' % name)
            return db


    def _get_dbxref(self,db,accession,description):

        # Get/Set Db instance: ref_db
        db = self._get_db(db)

        try:
            # Check if the dbxref is already registered
            dbxref = Dbxref.objects.get(db=db,accession=accession)
            return dbxref

        except ObjectDoesNotExist:

            # Save to the Dbxref model
            dbxref = Dbxref.objects.create(db=db,accession=accession,description=description)
            dbxref.save()
            return dbxref


    def _get_cvterm_dbxref(self,cvterm,dbxref,is_for_definition):

        try:
            # Check if the dbxref is already registered
            cvtermdbxref = CvtermDbxref.objects.get(cvterm=cvterm,dbxref=dbxref)
            return cvtermdbxref

        except ObjectDoesNotExist:

            # Save to the Dbxref model
            cvtermdbxref = CvtermDbxref.objects.create(cvterm=cvterm,
                                                       dbxref=dbxref,
                                                       is_for_definition=is_for_definition)
            cvtermdbxref.save()
            return cvtermdbxref


    def _process_def(self,cvterm,definition):

        text = ''

        '''
        Definition format:
        "text" [refdb:refcontent, refdb:refcontent]

        Definition format example:
        "A gene encoding an mRNA that has the stop codon redefined as pyrrolysine." [SO:xp]
        '''
        if definition:

            # Retrieve text and dbxrefs
            text,dbxrefs = definition.split('" [')
            text = re.sub(r'^"','',text)
            dbxrefs = re.sub(r'\]$','',dbxrefs)

            if dbxrefs:

                dbxrefs = dbxrefs.split(', ')

                # Save all dbxrefs
                for dbxref in dbxrefs:
                    ref_db,ref_content = dbxref.split(':',1)

                    if ref_db == 'http':
                        ref_db = 'URL'
                        ref_content = 'http:'+ref_content

                    # Get/Set Dbxref instance: ref_db,ref_content
                    dbxref = self._get_dbxref(ref_db,ref_content,'')

                    # Estabilish the cvterm and the dbxref relationship
                    self._get_cvterm_dbxref(cvterm,dbxref,1)

        cvterm.definition=text
        cvterm.save()
        return


    def _process_xref(self,cvterm,xref):

        text = ''

        if xref:

            ref_db,ref_content = xref.split(':',1)

            if ref_db == 'http':
                ref_db = 'URL'
                ref_content = 'http:'+ref_content

            # Get/Set Dbxref instance: ref_db,ref_content
            dbxref = self._get_dbxref(ref_db,ref_content,'')

            # Estabilish the cvterm and the dbxref relationship
            self._get_cvterm_dbxref(cvterm,dbxref,0)

        return


    def _process_synonym(self,cvterm,synonym):

        '''
        Definition format:
        "text" cvterm []

        Definition format example:
        "stop codon gained" EXACT []

        Attention:
        There are several cases that don't follow this format.
        These are being ignored for now.
        '''
        pattern = re.compile(r'^"(.+)" (\w+) \[\]$')
        matches = pattern.findall(synonym)

        if len(matches) != 1  or len(matches[0]) != 2:
            return

        synonym_text,synonym_type = matches[0]

        # Handling the synonym_type
        cv_type = self._get_cv('synonym_type','')
        dbxref_type = self._get_dbxref('internal',synonym_type.lower(),'')
        cvterm_type = self._get_cvterm(cv_type,synonym_type.lower(),'',dbxref_type,0)

        # Storing the synonym
        cvtermsynonym = Cvtermsynonym.objects.create(cvterm=cvterm,
                                                     synonym=synonym_text,
                                                     type_id=cvterm_type.cvterm_id)
        cvtermsynonym.save()
        return


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
            cv = Cv.objects.get(name=cv_name,definition=cv_definition)

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
            cv_property_type = self._get_cv('cvterm_property_type','')

            # Creating cvterm is_anti_symmetric to be used as type_id in cvtermprop
            dbxref_is_anti_symmetric = self._get_dbxref('internal','is_anti_symmetric','')
            cvterm_is_anti_symmetric = self._get_cvterm(cv_property_type,'is_anti_symmetric','',dbxref_is_anti_symmetric,0)

            # Creating cvterm is_transitive to be used as type_id in cvtermprop
            dbxref_is_transitive = self._get_dbxref('internal','is_transitive','')
            cvterm_is_transitive = self._get_cvterm(cv_property_type,'is_transitive','',dbxref_is_transitive,0)

            # Creating cvterm is_reflexive to be used as type_id in cvtermprop
            dbxref_is_reflexive = self._get_dbxref('internal','is_reflexive','')
            cvterm_is_reflexive = self._get_cvterm(cv_property_type,'is_reflexive','',dbxref_is_reflexive,0)

            # Creating cvterm comment to be used as type_id in cvtermprop
            dbxref_comment = self._get_dbxref('internal','comment','')
            cvterm_comment = self._get_cvterm(cv_property_type,'comment','',dbxref_comment,0)


            # Creating cv synonym_type
            cv_synonym_type = self._get_cv('synonym_type','')

            # Creating cvterm is_anti_symmetric to be used as type_id in cvtermprop
            dbxref_exact = self._get_dbxref('internal','exact','')
            cvterm_exact = self._get_cvterm(cv_property_type,'exact','',dbxref_exact,0)



            self.stdout.write('Loading typedefs')

            for data in G.graph['typedefs']:

                # Save the term to the Dbxref model
                aux_db,aux_accession = data.get('id').split(':')
                dbxref = self._get_dbxref(aux_db,aux_accession,'')

                # Save the term to the Cvterm model
                cvterm = self._get_cvterm(cv,data.get('name'),'',dbxref,1)

                # Load definition and dbxrefs
                definition = self._process_def(cvterm,data.get('def'))

                # Load is_anti_symmetric
                if data.get('is_anti_symmetric') is not None:
                    Cvtermprop.objects.create(cvterm=cvterm,
                                              type_id=cvterm_is_anti_symmetric.cvterm_id,
                                              value=1,
                                              rank=0)

                # Load is_reflexive
                if data.get('is_reflexive') is not None:
                    Cvtermprop.objects.create(cvterm=cvterm,
                                              type_id=cvterm_is_reflexive.cvterm_id,
                                              value=1,
                                              rank=0)

                # Load is_transitive
                if data.get('is_transitive') is not None:
                    Cvtermprop.objects.create(cvterm=cvterm,
                                              type_id=cvterm_is_transitive.cvterm_id,
                                              value=1,
                                              rank=0)

                # Load alt_ids
                if data.get('alt_id'):
                    for alt_id in data.get('alt_id'):
                        aux_db,aux_accession = alt_id.split(':')
                        dbxref_alt_id = self._get_dbxref(aux_db,aux_accession,'')
                        self._get_cvterm_dbxref(cvterm,dbxref_alt_id,0)

                # Load comment
                if data.get('comment'):
                    for comment in data.get('comment'):
                        Cvtermprop.objects.create(cvterm=cvterm,
                                                  type_id=cvterm_comment.cvterm_id,
                                                  value=comment,
                                                  rank=0)

                # Load xref
                if data.get('xref'):
                    for xref in data.get('xref'):
                        self._process_xref(cvterm,xref)

                # Load synonyms
                if data.get('synonym'):
                    for synonym in data.get('synonym'):
                        self._process_synonym(cvterm,synonym)



        self.stdout.write(self.style.SUCCESS('Done'))
