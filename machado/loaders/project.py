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
                 db: str=None) -> None:
        """Execute the init function."""
        try:
            self.db, created = Db.objects.get_or_create(name=db)
        except IntegrityError as e:
            self.db = None

    def store_project(self,
                      name: str) -> None:
        try:
            self.project, created = Project.objects.get_or_create(name=name)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_project_dbxref(self,
                             acc: str,
                             is_current: bool=True) -> None:
        """Store project_dbxref."""
        try:
            # for example, acc is the "GSExxxx" sample accession from GEO
            self.dbxref, created = Dbxref.objects.get_or_create(
                                                                accession=acc,
                                                                db=self.db)
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            self.project_dbxref, created = ProjectDbxref.objects.get_or_create(
                                       project=self.project,
                                       dbxref=self.dbxref,
                                       is_current=is_current)
        except IntegrityError as e:
            raise ImportingError(e)
