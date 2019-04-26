# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Biomaterial."""

from typing import Union

from django.db.utils import IntegrityError

from machado.loaders.common import retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.models import Biomaterial, Cvterm, Db, Dbxref, Organism
from machado.models import Treatment, BiomaterialTreatment, Biomaterialprop


class BiomaterialLoader(object):
    """Load biomaterial."""

    help = "Load biomaterial record."

    def __init__(self) -> None:
        """Execute the init function."""
        self.cvterm_contained_in = Cvterm.objects.get(
            name="contained in", cv__name="relationship"
        )

    def store_biomaterial(
        self,
        name: str,
        filename: str,
        db: str = None,
        acc: str = None,
        organism: Union[str, Organism] = None,
        description: str = None,
    ) -> Biomaterial:
        """Store biomaterial."""
        # db is not mandatory
        try:
            biodb, created = Db.objects.get_or_create(name=db)
        except IntegrityError:
            biodb = None
        # e.g.: acc is the "GSMxxxx" sample accession from GEO
        try:
            biodbxref, created = Dbxref.objects.get_or_create(db=biodb, accession=acc)
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
                defaults={"biosourceprovider_id": None},
            )
            self.store_biomaterialprop(
                biomaterial=biomaterial,
                type_id=self.cvterm_contained_in.cvterm_id,
                value=filename,
            )
        except IntegrityError as e:
            raise ImportingError(e)
        return biomaterial

    def store_biomaterial_treatment(
        self, biomaterial: Biomaterial, treatment: Treatment, rank: int = 0
    ) -> None:
        """Store biomaterial_treatment."""
        # treatment and biomaterial are mandatory
        try:
            (
                biomaterialtreatment,
                created,
            ) = BiomaterialTreatment.objects.get_or_create(
                biomaterial=biomaterial, treatment=treatment, rank=rank
            )
        except IntegrityError as e:
            raise ImportingError(e)

    def store_biomaterialprop(
        self, biomaterial: Biomaterial, type_id: int, value: str, rank: int = 0
    ) -> None:
        """Store analysisprop."""
        try:
            biomaterialprop, created = Biomaterialprop.objects.get_or_create(
                biomaterial=biomaterial, type_id=type_id, value=value, rank=rank
            )
        except IntegrityError as e:
            raise ImportingError(e)
