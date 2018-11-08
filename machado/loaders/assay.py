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
        # get database for assay (e.g.: "SRA" - from NCBI)
        try:
            self.db, created = Db.objects.get_or_create(name=db)
        except IntegrityError as e:
            self.db = None

        # will not use arraydesign nor operator
        self.db_null, created = Db.objects.get_or_create(name='null')
        self.dbxref_null, created = Dbxref.objects.get_or_create(
            db=self.db_null, accession='null')
        self.cv_null, created = Cv.objects.get_or_create(name='null')
        self.cvterm_null, created = Cvterm.objects.get_or_create(
            cv=self.cv_null,
            name='null',
            definition='',
            dbxref=self.dbxref_null,
            is_obsolete=0,
            is_relationshiptype=0)
        self.contact_null, created = Contact.objects.get_or_create(
            name='null',
            type_id=self.cvterm_null.cvterm_id)
        self.arraydesign_null, created = Arraydesign.objects.get_or_create(
            manufacturer_id=self.contact_null.contact_id,
            platformtype_id=self.cvterm_null.cvterm_id,
            name="Null")

    def store_assay(self,
                    name: str=None,
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
        try:
            self.dbxref, created = Dbxref.objects.get_or_create(
                                                       accession=acc,
                                                       db=self.db)
        except IntegrityError as e:
            self.dbxref = None
            #create assay object
        try:
            self.assay, created = Assay.objects.get_or_create(
                            arraydesign=self.arraydesign_null,
                            operator_id=self.contact_null.contact_id,
                            assaydate=assaydate,
                            dbxref=self.dbxref,
                            name=name,
                            description=description)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assay_project(self,
                            project: Union[str, Project]):
        """Store assay_project."""
        # project is mandatory
        if isinstance(project, Project):
            self.project = project
        else:
            try:
                self.project, created = Project.objects.get(name=project)
            except ObjectDoesNotExist as e:
                raise ImportingError(e)

        try:
            self.assayproject, created = AssayProject.objects.get_or_create(
                    assay=self.assay,
                    project=self.project)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assay_biomaterial(self,
                                biomaterial: Union[str, Biomaterial],
                                rank: int=0):
        """Store assay_biomaterial."""
        # biomaterial is mandatory
        if isinstance(biomaterial, Biomaterial):
            self.biomaterial = biomaterial
        else:
            try:
                self.biomaterial = Biomaterial.objects.get(name=biomaterial)
            except ObjectDoesNotExist as e:
                raise ImportingError(e)
        try:
            (self.assaybiomaterial,
                    created) = AssayBiomaterial.objects.get_or_create(
                    assay=self.assay,
                    biomaterial=self.biomaterial,
                    rank=rank)
        except IntegrityError as e:
            raise ImportingError(e)
