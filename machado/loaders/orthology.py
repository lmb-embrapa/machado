# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Orthology."""

from Bio.SeqRecord import SeqRecord
from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Db, Dbxref, Dbxrefprop, Feature, FeaturePub
from machado.models import PubDbxref, FeatureRelationship
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from hashlib import md5


class OrthologyLoader(object):
    """Load orthology records."""

    def __init__(self,
                 filename: str) -> None:
        """Execute the init function."""
        self.excluded = list()
        self.included = list()

    def store_feature_relationship(self,
                                   group: list) -> None:
        cvterm = "orthologous_to"
        text = "OrthoMCL"
        for member in group:
            tempgroup = group
            tempgroup.remove(member)
            for othermember in tempgroup:
                try:
                    frs, created = FeatureRelationship.objects.get_or_create(
                                            subject_id=member,
                                            object_id=othermember,
                                            type_id=cvterm,
                                            value=text,
                                            rank=0)
                except IntegrityError as e:
                    raise ImportingError(e)

    def store_orthologous_group(self,
                                name: str,
                                members: list) -> None:
        """Store Biopython SeqRecord."""
        try:
            # print(name, members)
            for ident in members:
                # check features for id
                try: 
                    feature = Feature.objects.get(uniquename=ident)
                    self.included.append(ident)
                except:
                    #feature does not exist
                    self.excluded.append(ident)
        except IntegrityError as e:
            raise ImportingError(e)

        # store relationship
        if len(self.included>1):
            try:
                store_feature_relationshipo(self.included)
            except IntegrityError as e:
                raise ImportingError(e)
