# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Orthology."""

from machado.loaders.exceptions import ImportingError
from machado.models import Organism
from machado.loaders.common import retrieve_ontology_term, retrieve_feature
from machado.loaders.feature import FeatureLoader
from django.db.utils import IntegrityError


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

        # register multispecies organism - needed by FeatureLoader
        # *It is not going to be used* : features are already registered and
        # bounded to an organism
        self.organism, created = Organism.objects.get_or_create(
                    abbreviation='multispecies',
                    genus='multispecies',
                    species='multispecies',
                    common_name='multispecies')
        # cv 'null' has cv_id==10 if you want to check
        source = 'null'
        self.featureloader = FeatureLoader(
                source=source,
                filename=self.filename,
                organism=self.organism)

    def store_orthologous_group(self,
                                members: list) -> None:
        """Retrieve Feature objects and store in list and then store group."""
        try:
            for ident in members:
                # check if features are registered
                # need to use cvterm 'polypeptide' as orthology is derived from
                # protein sequences.
                feature = retrieve_feature(
                        featureacc=ident,
                        cvterm="polypeptide",
                        ontology="sequence")
                if feature is not None:
                    self.included.append(feature)
                else:
                    self.excluded.append(ident)
        except IntegrityError as e:
            raise ImportingError(e)
        if len(self.included) > 1:
            try:
                # self.store_feature_relationship(group=self.included)
                self.featureloader.store_feature_relationships_group(
                        group=self.included,
                        term=self.cvterm_orthology,
                        value=self.name)
            except IntegrityError as e:
                raise ImportingError(e)
