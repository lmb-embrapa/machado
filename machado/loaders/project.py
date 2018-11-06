# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Project."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Biomaterial, Db, Dbxref
from machado.models import Cv, Cvterm, Project, Projectprop, ProjectDbxref
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class ProjectLoader(object):
    """Load project."""

    help = 'Load project record.'

    def __init__(self,
                 projectdb:str=None) -> None:
        """Execute the init function."""
        if projectdb:
            try:
                self.db, created = Db.objects.get_or_create(name=projectdb)
            except IntegrityError as e:
                raise ImportingError(e)
        # get cvterm for store filename in Projectprop
        try:
            self.cvterm_contained = Cvterm.objects.get(name='contained in')
        except IntegrityError as e:
            raise ImportingError(e)

    def store_project(self,
                      name:str) -> None:
        try:
            self.project = Project.objects.create(name=name)
        except IntegrityError as e:
            raise ImportingError(e)


    def store_projectprop(self,
                          filename:str) -> None:
        """Store project_prop."""
        if self.project:
            try:
                self.projectprop = Projectprop.objects.create(
                        project=self.project,
                        value=filename,
                        type_id=self.cvterm_contained.cvterm_id,
                        rank=0)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            raise ImportingError(
                "Parent not found: Project is required to store "
                "an Projectprop.")


    def store_project_dbxref(self,
                             acc:str,
                             is_current: bool=True) -> None:
        """Store project_dbxref."""
        if (self.project and self.db):
            try:
                # for example, acc is the "GSExxxx" sample accession from GEO
                self.dbxref, created = Dbxref.objects.get_or_create(
                                                                    accession=acc,
                                                                    db=self.db)
                self.project_dbxref = ProjectDbxref.objects.create(
                                           project=self.project,
                                           dbxref=self.dbxref,
                                           is_current=is_current)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            raise ImportingError(
                "Parent not found: Project and Projectdb are required "
                "to store a ProjectDbxref.")
