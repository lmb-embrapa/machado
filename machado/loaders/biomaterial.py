# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Biomaterial."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Biomaterial, Db, Dbxref, Organism 
from machado.models import Cv, Cvterm, Treatment, BiomaterialTreatment
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from typing import Dict, List, Set, Union


class BiomaterialLoader(object):
    """Load biomaterial."""

    help = 'Load biomaterial record.'

    def __init__(self,
                 db: str=None) -> None:

        """Execute the init function."""
        # get database for biomaterial (e.g.: "GEO" - from NCBI)
        if db:
            try:
                self.db, created = Db.objects.get_or_create(name=db)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            self.db = None

    def store_biomaterial(self,
                          name:str,
                          acc:str=None,
                          organism: Union[str, Organism]=None,
                          description:str=None) -> None:

        """Store biomaterial."""
        # organism
        if organism:
            if isinstance(organism, Organism):
                self.organism = organism
            else:
                try:
                    self.organism = retrieve_organism(organism)
                except IntegrityError as e:
                    raise ImportingError(e)
        else:
            self.organism, created  = Organism.object.get_or_create(
                    genus="null",
                    species="null")

        # for example, acc is the "GSMxxxx" sample accession from GEO
        if acc:
            try:
                self.dbxref, created = Dbxref.objects.get_or_create(
                                                           db=self.db,
                                                           accession=acc)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            self.dbxref, created = Dbxref.objects.get_or_create(
                                             db=self.db,
                                             accession='null')

        # get cvterm for condition - TODO
        # create treatment table
        # but before, import required ontology,
        # check http://obi-ontology.org/
        # or: https://www.bioontology.org/
        # #######
        # self.name = tissue
        # self.description = condition
        # try:
        #     self.cvterm = retrieve_ontology_term(ontology, condition)
        # except IntegrityError as e:
        #     raise ImportingError(e)

        # finally, create biomaterial entry
        try:
            self.biomaterial = Biomaterial.objects.create(
                                    taxon_id=self.organism.organism_id,
                                    dbxref=self.dbxref,
                                    name=name,
                                    description=description)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_biomaterial_treatment(self,
                                    treatment: Union[str, Biomaterial],
                                    rank:int=0
                                    ) -> None:
        """Store biomaterial_treatment."""
        if isinstance(treatment, Treatment):
            self.treatment = treatment
        else:
            try:
                self.treatment = Treatment.objects.get(
                        name=treatment,
                        biomaterial=self.biomaterial)
            except IntegrityError as e:
                raise ImportingError(e)
        # finally, create biomaterial_treatment entry
        try:
            self.biomaterial_treatment = BiomaterialTreatment.objects.create(
                                    biomaterial=self.biomaterial,
                                    treatment=self.treatment,
                                    rank=rank)
        except IntegrityError as e:
            raise ImportingError(e)
