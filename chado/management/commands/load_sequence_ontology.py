from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv,Cvprop,Cvterm,CvtermDbxref,Cvtermprop,CvtermRelationship,Cvtermsynonym,Db,Dbxref
from obo import read_obo
import re
import pprint


class Command(BaseCommand):
    help = 'Load Sequence Ontology'


    def add_arguments(self, parser):
        parser.add_argument("--so", help="Sequence Ontology file obo. Available at https://github.com/The-Sequence-Ontology/SO-Ontologies", required = True, type=str)


    def _get_cv(self,name,definition):

        try:
            # Check if the cv is already registered
            cv = Cv.objects.get(name=name,definition=definition)
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

        cvterm.definition=definition
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
        with open(options['so']) as obo_file:
            G = read_obo(obo_file)

        cv_name = G.graph['default-namespace'][0]
        cv_definition=G.graph['date']

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
            cv_relationship = self._get_cv('cvterm_relationship','')
            cv_property_type = self._get_cv('cvterm_property_type','')


            # Creating cvterm is_symmetric to be used as type_id in cvtermprop
            dbxref_is_symmetric = self._get_dbxref('internal','is_symmetric','')
            cvterm_is_symmetric = self._get_cvterm(cv_property_type,'is_symmetric','',dbxref_is_symmetric,0)

            # Creating cvterm is_transitive to be used as type_id in cvtermprop
            dbxref_is_transitive = self._get_dbxref('internal','is_transitive','')
            cvterm_is_transitive = self._get_cvterm(cv_property_type,'is_transitive','',dbxref_is_transitive,0)


            self.stdout.write('Loading typedefs')

            # Load typedefs as Dbxrefs and Cvterm
            for typedef in G.graph['typedefs']:
                dbxref_typedef = self._get_dbxref('_global',typedef['id'],typedef.get('def'))
                cvterm_typedef = self._get_cvterm(cv,typedef.get('id'),typedef.get('def'),dbxref_typedef,1)

                # Load is_symmetric
                if typedef.get('is_symmetric') is not None:
                    Cvtermprop.objects.create(cvterm=cvterm_typedef,
                                              type_id=cvterm_is_symmetric.cvterm_id,
                                              value=1,
                                              rank=0)
                # Load is_transitive
                if typedef.get('is_transitive') is not None:
                    Cvtermprop.objects.create(cvterm=cvterm_typedef,
                                              type_id=cvterm_is_transitive.cvterm_id,
                                              value=1,
                                              rank=0)


            self.stdout.write('Loading terms')

            # Creating cvterm comment to be used as type_id in cvtermprop
            dbxref_comment = self._get_dbxref('internal','comment','')
            cvterm_comment = self._get_cvterm(cv_property_type,'comment','',dbxref_comment,0)

            for n,data in G.nodes(data=True):

                # Save the term to the Dbxref model
                aux_db,aux_accession = n.split(':')
                dbxref = self._get_dbxref(aux_db,aux_accession,'')

                # Save the term to the Cvterm model
                cvterm = self._get_cvterm(cv,data.get('name'),'',dbxref,0)

                # Load definition and dbxrefs
                definition = self._process_def(cvterm,data.get('def'))

                # Load alt_ids
                if data.get('alt_id'):
                    for alt_id in data.get('alt_id'):
                        aux_db,aux_accession = alt_id.split(':')
                        dbxref_alt_id = self._get_dbxref(aux_db,aux_accession,'')
                        self._get_cvterm_dbxref(cvterm,dbxref_alt_id,0)

                # Load comment
                if data.get('comment'):
                    Cvtermprop.objects.create(cvterm=cvterm,
                                              type_id=cvterm_comment.cvterm_id,
                                              value=data.get('comment'),
                                              rank=0)

                # Load xref
                if data.get('xref'):
                    for xref in data.get('xref'):
                        self._process_xref(cvterm,xref)

                # Load synonyms
                if data.get('synonym'):
                    for synonym in data.get('synonym'):
                        self._process_synonym(cvterm,synonym)


            self.stdout.write('Loading relationships')

            # Creating term is_a to be used as type_id in cvterm_relationship
            cv_relationship = self._get_cv('cvterm_relationship','')
            dbxref_is_a = self._get_dbxref('OBO_REL','is_a','')
            cvterm_is_a = self._get_cvterm(cv_relationship,'is_a','',dbxref_is_a,1)


            for u,v,type in G.edges(keys=True):

                # Get the subject cvterm
                subject_db_name,subject_dbxref_accession = u.split(':')
                subject_db = Db.objects.get(name=subject_db_name)
                subject_dbxref = Dbxref.objects.get(accession=subject_dbxref_accession,db=subject_db)
                subject_cvterm = Cvterm.objects.get(cv=cv,dbxref=subject_dbxref)

                # Get the object cvterm
                object_db_name,object_dbxref_accession = v.split(':')
                object_db = Db.objects.get(name=object_db_name)
                object_dbxref = Dbxref.objects.get(accession=object_dbxref_accession,db=object_db)
                object_cvterm = Cvterm.objects.get(cv=cv,dbxref=object_dbxref)

                if type == 'is_a':
                    type_cvterm = cvterm_is_a
                else:
                    type_db = Db.objects.get(name='_global')
                    type_dbxref = Dbxref.objects.get(accession=type,db=type_db)
                    type_cvterm = Cvterm.objects.get(cv=cv,dbxref=type_dbxref)

                cvrel = CvtermRelationship.objects.create(type_id=type_cvterm.cvterm_id,
                                                          subject_id=subject_cvterm.cvterm_id,
                                                          object_id=object_cvterm.cvterm_id)
                cvrel.save()

        self.stdout.write(self.style.SUCCESS('Done'))
