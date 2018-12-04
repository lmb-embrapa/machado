# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Biomaterial."""

from machado.loaders.common import retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.models import Biomaterial, Db, Dbxref, Organism
from machado.models import Treatment, BiomaterialTreatment
from django.db.utils import IntegrityError
from typing import Union


class BiomaterialLoader(object):
    """Load biomaterial."""

    help = 'Load biomaterial record.'

    def store_biomaterial(self,
                          name: str,
                          db: str = None,
                          acc: str = None,
                          organism: Union[str, Organism] = None,
                          description: str = None) -> Biomaterial:
        """Store biomaterial."""
        # db is not mandatory
        try:
            biodb, created = Db.objects.get_or_create(name=db)
        except IntegrityError:
            biodb = None
        # e.g.: acc is the "GSMxxxx" sample accession from GEO
        try:
            biodbxref, created = Dbxref.objects.get_or_create(
                                                       db=biodb,
                                                       accession=acc)
        except IntegrityError:
            biodbxref = None
        # organism is mandatory
        if isinstance(organism, Organism):
            organism_id = organism.organism_id
        else:
            try:
                self.organism = retrieve_organism(organism)
                organism_id = self.organism.organism_id
            except IntegrityError:
                organism_id = None

        # get cvterm for condition - TODO
        # import required ontology,
        # check http://obi-ontology.org/
        # or: https://www.bioontology.org/
        # #######
        try:
            # made name mandatory (it is not regarding the schema definition)
            biomaterial, created = Biomaterial.objects.get_or_create(
                                        name=name,
                                        taxon_id=organism_id,
                                        dbxref=biodbxref,
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
                                    rank: int = 0) -> None:
        """Store biomaterial_treatment."""
        # treatment and biomaterial are mandatory
        try:
            (biomaterialtreatment,
             created) = BiomaterialTreatment.objects.get_or_create(
                                biomaterial=biomaterial,
                                treatment=treatment,
                                rank=rank)
        except IntegrityError as e:
            raise ImportingError(e)
