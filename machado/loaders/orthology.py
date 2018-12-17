# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Orthology."""

from machado.loaders.exceptions import ImportingError
from machado.models import Feature
from machado.models import FeatureRelationship, FeatureRelationshipprop
from machado.loaders.common import retrieve_ontology_term
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class OrthologyLoader(object):
    """Load orthology records."""

    help = 'Load orthology records.'

    def __init__(self,
                 name: str,
                 filename: str) -> None:
        """Execute the init function."""
        self.excluded = list()
        self.included = list()
        self.name = name
        self.filename = filename

        # get cvterm for orthology
        try:
            self.cvterm_orthology = retrieve_ontology_term(
                ontology='relationship',
                term="in orthology relationship with")
        except IntegrityError as e:
            raise ImportingError(e)

        # get cvterm for contained in
        try:
            self.cvterm_contained_in = retrieve_ontology_term(
                ontology='relationship', term='contained in')
        except IntegrityError as e:
            raise ImportingError(e)

    def store_feature_relationship(self,
                                   group: list) -> None:
        """Store Feature Relationship."""
        for member in group:
            tempgroup = group.copy()
            tempgroup.remove(member)
            for othermember in tempgroup:
                try:
                    feature_relationship = FeatureRelationship.objects.create(
                                    subject_id=member.feature_id,
                                    object_id=othermember.feature_id,
                                    type_id=self.cvterm_orthology.cvterm_id,
                                    value=self.name,
                                    rank=0)
                except IntegrityError as e:
                    raise ImportingError(e)
                try:
                    FeatureRelationshipprop.objects.create(
                                feature_relationship=feature_relationship,
                                type_id=self.cvterm_contained_in.cvterm_id,
                                value=self.filename,
                                rank=0)
                except IntegrityError as e:
                    raise ImportingError(e)

    def store_orthologous_group(self,
                                members: list) -> None:
        """Retrieve Feature objects and store in list and then store group."""
        try:
            for ident in members:
                # check features for id
                try:
                    feature = Feature.objects.get(uniquename=ident)
                    self.included.append(feature)
                except ObjectDoesNotExist:
                    # feature does not exist
                    self.excluded.append(ident)
        except IntegrityError as e:
            raise ImportingError(e)
        if len(self.included) > 1:
            try:
                self.store_feature_relationship(self.included)
            except IntegrityError as e:
                raise ImportingError(e)
