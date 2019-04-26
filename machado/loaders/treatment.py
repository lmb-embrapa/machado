# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Treatment."""

from django.db.utils import IntegrityError

from machado.loaders.exceptions import ImportingError
from machado.models import Biomaterial, Db, Dbxref
from machado.models import Cv, Cvterm, Treatment


class TreatmentLoader(object):
    """Load treatment."""

    help = "Load treatment record."

    def __init__(self) -> None:
        """Execute the init function."""
        # will not use type_id - TODO - load specific ontology for treatment
        db_null, created = Db.objects.get_or_create(name="null")
        dbxref_null, created = Dbxref.objects.get_or_create(
            db=db_null, accession="null"
        )
        cv_null, created = Cv.objects.get_or_create(name="null")
        self.cvterm_null, created = Cvterm.objects.get_or_create(
            cv=cv_null,
            name="null",
            definition="",
            dbxref=dbxref_null,
            is_obsolete=0,
            is_relationshiptype=0,
        )

    def store_treatment(
        self, name: str, biomaterial: Biomaterial, rank: int = 0
    ) -> Treatment:
        """Store treatment."""
        try:
            treatment, created = Treatment.objects.get_or_create(
                biomaterial=biomaterial,
                type_id=self.cvterm_null.cvterm_id,
                name=name,
                rank=rank,
            )
        except IntegrityError as e:
            raise ImportingError(e)
        return treatment
