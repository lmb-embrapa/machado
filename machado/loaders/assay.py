# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Assay."""

from datetime import datetime

from django.db.utils import IntegrityError

from machado.loaders.exceptions import ImportingError
from machado.models import Arraydesign, Contact
from machado.models import Assay, AssayBiomaterial, AssayProject, Assayprop
from machado.models import Biomaterial, Db, Dbxref
from machado.models import Cv, Cvterm, Project


class AssayLoader(object):
    """Load Assay."""

    help = "Load assay record."

    def __init__(self) -> None:
        """Execute the init function."""
        # will not use arraydesign nor operator
        db_null, created = Db.objects.get_or_create(name="null")
        dbxref_null, created = Dbxref.objects.get_or_create(
            db=db_null, accession="null"
        )
        cv_null, created = Cv.objects.get_or_create(name="null")
        cvterm_null, created = Cvterm.objects.get_or_create(
            cv=cv_null,
            name="null",
            definition="",
            dbxref=dbxref_null,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        self.contact_null, created = Contact.objects.get_or_create(
            name="null", type_id=cvterm_null.cvterm_id
        )
        self.arraydesign_null, created = Arraydesign.objects.get_or_create(
            manufacturer_id=self.contact_null.contact_id,
            platformtype_id=cvterm_null.cvterm_id,
            name="Null",
        )
        self.cvterm_contained_in = Cvterm.objects.get(
            name="contained in", cv__name="relationship"
        )

    def store_assay(
        self,
        name: str,
        filename: str,
        db: str = None,
        acc: str = None,
        assaydate: str = None,
        description: str = None,
    ) -> Assay:
        """Store assay."""
        # get database for assay (e.g.: "SRA" - from NCBI)
        try:
            assaydb, created = Db.objects.get_or_create(name=db)
        except IntegrityError:
            assaydb = None
        # for example, acc is the "SRRxxxx" experiment accession from SRA
        try:
            assaydbxref, created = Dbxref.objects.get_or_create(
                accession=acc, db=assaydb
            )
        except IntegrityError:
            assaydbxref = None
        if assaydate:
            # format is mandatory, e.g.: Oct-16-2016)
            # in settings.py set USE_TZ = False
            date_format = "%b-%d-%Y"
            assaydate = datetime.strptime(assaydate, date_format)
        # create assay object
        try:
            assay, created = Assay.objects.get_or_create(
                arraydesign=self.arraydesign_null,
                assaydate=assaydate,
                operator_id=self.contact_null.contact_id,
                name=name,
                dbxref=assaydbxref,
                description=description,
                defaults={
                    "protocol_id": None,
                    "arrayidentifier": None,
                    "arraybatchidentifier": None,
                },
            )
            self.store_assayprop(
                assay=assay, type_id=self.cvterm_contained_in.cvterm_id, value=filename
            )
        except IntegrityError as e:
            raise ImportingError(e)
        return assay

    def store_assay_project(self, assay: Assay, project: Project) -> None:
        """Store assay_project."""
        try:
            assayproject, created = AssayProject.objects.get_or_create(
                assay=assay, project=project
            )
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assay_biomaterial(
        self, assay: Assay, biomaterial: Biomaterial, rank: int = 0
    ) -> None:
        """Store assay_biomaterial."""
        try:
            (assaybiomaterial, created) = AssayBiomaterial.objects.get_or_create(
                assay=assay,
                biomaterial=biomaterial,
                rank=rank,
                defaults={"channel_id": None},
            )
        except IntegrityError as e:
            raise ImportingError(e)

    def store_assayprop(
        self, assay: Assay, type_id: int, value: str, rank: int = 0
    ) -> None:
        """Store analysisprop."""
        try:
            Assayprop.objects.create(
                assay=assay, type_id=type_id, value=value, rank=rank
            )
        except IntegrityError as e:
            raise ImportingError(e)
