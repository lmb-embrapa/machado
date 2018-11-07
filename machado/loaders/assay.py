# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Assay."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Assay, AssayBiomaterial, AssayProject
from machado.models import Biomaterial, Db, Dbxref
from machado.models import Arraydesign, Protocol, Contact
from machado.models import Cv, Cvterm, Project
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from typing import Dict, List, Set, Union
from datetime import datetime

class AssayLoader(object):
    """Load Assay."""

    help = 'Load assay record.'

    def __init__(self,
                 db: str=None) -> None:
        """Execute the init function."""
        if db:
            # get database for assay (e.g.: "SRA" - from NCBI)
            try:
                self.db, created = Db.objects.get_or_create(name=db)
            except IntegrityError as e:
                raise ImportingError(e)

        # need to create several null fields for dummy arraydesign table
        self.db_null, created = Db.objects.get_or_create(name='null')
        self.null_dbxref, created = Dbxref.objects.get_or_create(
            db=self.db_null, accession='null')
        self.null_cv, created = Cv.objects.get_or_create(name='null')
        self.null_cvterm, created = Cvterm.objects.get_or_create(
            cv=self.null_cv,
            name='null',
            definition='',
            dbxref=self.null_dbxref,
            is_obsolete=0,
            is_relationshiptype=0)

        # will not use contact's operator
        self.null_contact, created = Contact.objects.get_or_create(
            name='null',
            type_id=self.null_cvterm.cvterm_id)
        # will not use arraydesign
        self.arraydesign, created = Arraydesign.objects.get_or_create(
            manufacturer_id=self.null_contact.contact_id,
            platformtype_id=self.null_cvterm.cvterm_id,
            name="Null")

        # initialize self.dbxref
        self.dbxref = self.null_dbxref

    def store_assay(self,
                    name: str,
                    acc: str=None,
                    assaydate: str=None,
                    description: str=None) -> None:
        """Store assay."""

        if assaydate:
            # format date mandatory, e.g.: Oct-16-2016)
            # in settings.py set USE_TZ = False
            date_format = '%b-%d-%Y'
            assaydate = datetime.strptime(assaydate, date_format)
        # for example, acc is the "SRRxxxx" experiment accession from SRA
        if acc:
            try:
                self.dbxref, created = Dbxref.objects.get_or_create(
                                                           accession=acc,
                                                           db=self.db)
            except IntegrityError as e:
                raise ImportingError(e)
            #create assay object
        try:
            self.assay = Assay.objects.create(
                            arraydesign=self.arraydesign,
                            operator_id=self.null_contact.contact_id,
                            assaydate=assaydate,
                            dbxref=self.dbxref,
                            name=name,
                            description=description)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assay_project(self,
                            project:Union[str, Project]):
        """Store assay_project."""
        if isinstance(project, Project):
            self.project = project
        else:
            try:
                self.project, created = Project.objects.get(name=project)
            except ObjectDoesNotExist as e:
                raise ImportingError(e)

        try:
            self.assayproject = AssayProject.objects.create(
                    assay=self.assay,
                    project=self.project)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assay_biomaterial(self,
                                biomaterial:Union[str, Biomaterial]):
        """Store assay_biomaterial."""
        if isinstance(biomaterial, Biomaterial):
            self.biomaterial = biomaterial
        else:
            try:
                self.biomaterial = Biomaterial.objects.get(name=biomaterial)
            except ObjectDoesNotExist as e:
                raise ImportingError(e)

        try:
            self.assaybiomaterial = AssayBiomaterial.objects.create(
                    assay=self.assay,
                    biomaterial=self.biomaterial,
                    rank=0)
        except IntegrityError as e:
            raise ImportingError(e)
