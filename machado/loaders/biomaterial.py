# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Biomaterial."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Db, Dbxref
from machado.models import Biomaterial, Db, Dbxref
from machado.models import Cv, Cvterm
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class BiomaterialLoader(object):
    """Load biomaterial."""

    help = 'Load biomaterial record.'

    def __init__(self,
                 db: Union[str, Db]) -> None:

        """Execute the init function."""
        # get database for biomaterial (e.g.: "GEO" - from NCBI)
        if isinstance(db, Db):
            self.db = db
        else:
            try:
                self.db = Db.objects.create(name=db)
            except IntegrityError as e:
                raise ImportingError(e)

    def store_biomaterial(self,
                          acc: Union[str, Dbxref],
                          organism: Union[str, Organism],
                          tissue:str,
                          condition:str) -> None:
        # for example, acc is the "GSMxxxx" sample accession from GEO
        if isinstance(acc, Dbxref):
            self.dbxref = acc
        else:
            try:
                self.dbxref = Dbxref.objects.create(accession=acc,
                                                    db=self.db,
                                                    version=None)
            except IntegrityError as e:
                raise ImportingError(e)
        # organism
        if isinstance(organism, Organism):
            self.organism = organism
        else:
            try:
                self.organism = retrieve_organism(organism)
            except IntegrityError as e:
                raise ImportingError(e)

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
        try:
            biomaterial = Biomaterial.objects.create(
                                    taxon_id=self.organism.organism_id,
                                    dbxref=self.dbxref,
                                    name=tissue,
                                    description=condition)
        except IntegrityError as e:
            raise ImportingError(e)
