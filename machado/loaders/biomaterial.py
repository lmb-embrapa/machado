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
        try:
            self.db, created = Db.objects.get_or_create(name=db)
        except IntegrityError as e:
            self.db = None

    def store_biomaterial(self,
                          name:str,
                          acc:str=None,
                          organism: Union[str, Organism]=None,
                          description:str=None) -> Biomaterial:

        """Store biomaterial."""
        # organism is mandatory
        if isinstance(organism, Organism):
            organism_id = organism.organism_id
        else:
            try:
                self.organism = retrieve_organism(organism)
                organism_id = self.organism.organism_id
            except IntegrityError as e:
                organism_id = None
        # e.g.: acc is the "GSMxxxx" sample accession from GEO
        try:
            dbxref, created = Dbxref.objects.get_or_create(
                                                       db=self.db,
                                                       accession=acc)
        except IntegrityError as e:
            dbxref = None

        # get cvterm for condition - TODO
        # import required ontology,
        # check http://obi-ontology.org/
        # or: https://www.bioontology.org/
        # #######

        #create biomaterial entry
        try:
            biomaterial, created = Biomaterial.objects.get_or_create(
                                        taxon_id=organism_id,
                                        dbxref=dbxref,
                                        name=name,
                                        description=description,
                                        defaults={
                                            'biosourceprovider_id': None,
                                            }
                                        )
        except IntegrityError as e:
            raise ImportingError(e)
        return biomaterial

    def store_biomaterial_treatment(self,
                                    biomaterial: Biomaterial,
                                    treatment: Treatment,
                                    rank: int=0) -> None:
        """Store biomaterial_treatment."""
        # treatment is mandatory
        try:
            (biomaterialtreatment,
                    created) = BiomaterialTreatment.objects.get_or_create(
                                biomaterial=biomaterial,
                                treatment=treatment,
                                rank=rank)
        except IntegrityError as e:
            raise ImportingError(e)
