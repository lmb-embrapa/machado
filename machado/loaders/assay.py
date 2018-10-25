# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Assay."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Db, Dbxref
from machado.models import Biomaterial, Db, Dbxref
from machado.models import Assay, Arraydesign, Protocol, Contact
from machado.models import Cv, Cvterm
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from datetime import datetime


class AssayLoader(object):
    """Load Assay."""

    help = 'Load assay record.'

    def __init__(self,
                 db: Union[str, Db]) -> None:
        """Execute the init function."""
        # get database for assay (e.g.: "SRA" - from NCBI)
        if isinstance(db, Db):
            self.db = db
        else:
            try:
                self.db = Db.objects.create(name=db)
            except IntegrityError as e:
                raise ImportingError(e)

        # need to create several null fields for dependency tables
        self.db_null, created = Db.objects.get_or_create(name='null')
        null_dbxref, created = Dbxref.objects.get_or_create(
            db=self.db_null, accession='null')
        null_cv, created = Cv.objects.get_or_create(name='null')
        null_cvterm, created = Cvterm.objects.get_or_create(
            cv=null_cv,
            name='null',
            definition='',
            dbxref=null_dbxref,
            is_obsolete=0,
            is_relationshiptype=0)
        null_contact, created = Contact.objects.get_or_create(
            name='null',
            type_id=null_cvterm.cvterm_id)
        # will not use arraydesign
        self.arraydesign, created = Arraydesign.objects.get_or_create(
            manufacturer_id=null_contact.contact_id,
            platformtype_id=null_cvterm.cvterm_id,
            name="Null")

    def store_assay(self,
                    acc: Union[str, Dbxref],
                    date:str,
                    name:str,
                    description:str) -> None:
        # format date mandatory, e.g.: Oct-16-2016)
        date_format = '%b-%d-%Y'
        formatted_date = datetime.strptime(date, date_format)
        # for example, acc is the "SRRxxxx" experiment accession from SRA
        if isinstance(acc, Dbxref):
            self.dbxref = acc
        else:
            try:
                self.dbxref = Dbxref.objects.create(accession=acc,
                                                    db=self.db,
                                                    version=None)
            except IntegrityError as e:
                raise ImportingError(e)
        #create assay object
        try:
            self.assay = Assay.objects.create(
                            arraydesign=self.arraydesign,
                            operator_id=null_contact.contact_id,
                            assaydate=formatted_date,
                            dbxref=self.dbxref,
                            name=name,
                            description=description)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assay_project(self,
                            project:object):
        if self.assay:
            try:
                self.assayproject = AssayProject.objects.create(
                        assay=self.assay,
                        project=project)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            raise ImportingError(
                "Parent not found: Assay is required to store "
                "an assay_project.")

    def store_assay_biomaterial(self,
                                biomaterial:object):
        if self.assay:
            try:
                self.assaybiomaterial = AssayBiomaterial.objects.create(
                        assay=self.assay,
                        biomaterial=biomaterial,
                        rank=0)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            raise ImportingError(
                "Parent not found: Assay is required to store "
                "an assay_project.")



