# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Treatment."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Biomaterial, Db, Dbxref, Organism
from machado.models import Cv, Cvterm, Treatment
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from typing import Dict, List, Set, Union


class TreatmentLoader(object):
    """Load treatment."""

    help = 'Load treatment record.'

    def __init__(self,
                 cv: str=None,
                 cvterm: str=None) -> None:

        """Execute the init function."""
        # get database for biomaterial (e.g.: "GEO" - from NCBI)
        if cv and cvterm:
            try:
                self.cv = Cv.objects.get(name=cv)
                self.cvterm = Cvterm.objects.get(
                                                 name=cvterm,
                                                 cv=self.cv
                                                )
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            self.db, created = Db.objects.get_or_create(name='null')
            self.dbxref, created = Dbxref.objects.get_or_create(
                db=self.db, accession='null')
            self.cv, created = Cv.objects.get_or_create(name='null')
            self.cvterm, created = Cvterm.objects.get_or_create(
                cv=self.cv,
                name='null',
                definition='',
                dbxref=self.dbxref,
                is_obsolete=0,
                is_relationshiptype=0)

    def store_treatment(self,
                        name:str,
                        biomaterial: Union[str, Biomaterial],
                        rank: int=0) -> None:
        """Store treatment."""
        if isinstance(biomaterial, Biomaterial):
            self.biomaterial = biomaterial
        else:
            try:
                self.biomaterial = Biomaterial.objects.get_or_create(
                        name=biomaterial)
            except IntegrityError as e:
                raise ImportingError(e)
        # TODO - implement protocol input
        try:
            self.treatment = Treatment.objects.create(
                                    biomaterial=self.biomaterial,
                                    type_id=self.cvterm.cvterm_id,
                                    name=name,
                                    rank=rank
                                    )
        except IntegrityError as e:
            raise ImportingError(e)
