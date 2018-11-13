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
    def __init__(self) -> None:
        # will not use arraydesign nor operator
        db_null, created = Db.objects.get_or_create(name='null')
        dbxref_null, created = Dbxref.objects.get_or_create(
            db=db_null, accession='null')
        cv_null, created = Cv.objects.get_or_create(name='null')
        cvterm_null, created = Cvterm.objects.get_or_create(
            cv=cv_null,
            name='null',
            definition='',
            dbxref=dbxref_null,
            is_obsolete=0,
            is_relationshiptype=0)
        self.contact_null, created = Contact.objects.get_or_create(
            name='null',
            type_id=cvterm_null.cvterm_id)
        self.arraydesign_null, created = Arraydesign.objects.get_or_create(
            manufacturer_id=self.contact_null.contact_id,
            platformtype_id=cvterm_null.cvterm_id,
            name="Null")

    def store_assay(self,
                    name: str,
                    db: str=None,
                    acc: str=None,
                    assaydate: str=None,
                    description: str=None) -> Assay:
        """Store assay."""

        # get database for assay (e.g.: "SRA" - from NCBI)
        try:
            assaydb, created = Db.objects.get_or_create(name=db)
        except IntegrityError as e:
            assaydb = None
        # for example, acc is the "SRRxxxx" experiment accession from SRA
        try:
            assaydbxref, created = Dbxref.objects.get_or_create(
                                                       accession=acc,
                                                       db=assaydb)
        except IntegrityError as e:
            assaydbxref = None
        if assaydate:
            # format is mandatory, e.g.: Oct-16-2016)
            # in settings.py set USE_TZ = False
            date_format = '%b-%d-%Y'
            assaydate = datetime.strptime(assaydate, date_format)
        #create assay object
        try:
            assay, created = Assay.objects.get_or_create(
                                    arraydesign=self.arraydesign_null,
                                    assaydate=assaydate,
                                    operator_id=self.contact_null.contact_id,
                                    name=name,
                                    dbxref=assaydbxref,
                                    description=description,
                                    defaults={
                                        'protocol_id': None,
                                        'arrayidentifier': None,
                                        'arraybatchidentifier': None,
                                        }
                                    )
        except IntegrityError as e:
            raise ImportingError(e)
        return assay

    def store_assay_project(self,
                            assay: Assay,
                            project: Project) -> None:
        """Store assay_project."""
        try:
            assayproject, created = AssayProject.objects.get_or_create(
                    assay=assay,
                    project=project)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assay_biomaterial(self,
                                assay: Assay,
                                biomaterial: Biomaterial,
                                rank: int=0) -> None:
        """Store assay_biomaterial."""
        try:
            (assaybiomaterial,
                    created) = AssayBiomaterial.objects.get_or_create(
                    assay=assay,
                    biomaterial=biomaterial,
                    rank=rank,
                    defaults={
                        'channel_id': None}
                    )
        except IntegrityError as e:
            raise ImportingError(e)
