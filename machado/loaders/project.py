# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Project."""

from machado.loaders.exceptions import ImportingError
from machado.models import Db, Dbxref
from machado.models import Project, ProjectDbxref
from django.db.utils import IntegrityError


class ProjectLoader(object):
    """Load project."""

    help = 'Load project record.'

    def store_project(self,
                      name: str) -> Project:
        """Store project."""
        try:
            project, created = Project.objects.get_or_create(name=name)
        except IntegrityError as e:
            raise ImportingError(e)
        return project

    def store_project_dbxref(self,
                             project: Project,
                             acc: str,
                             db: str,
                             is_current: bool = True) -> None:
        """Store project_dbxref."""
        # db is mandatory
        try:
            projectdb, created = Db.objects.get_or_create(name=db)
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            # for example, acc is the "GSExxxx" sample accession from GEO
            dbxref, created = Dbxref.objects.get_or_create(
                                                           accession=acc,
                                                           db=projectdb)
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            project_dbxref, created = ProjectDbxref.objects.get_or_create(
                                       project=project,
                                       dbxref=dbxref,
                                       is_current=is_current)
        except IntegrityError as e:
            raise ImportingError(e)
