# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Project."""

from machado.loaders.common import retrieve_organism, retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from machado.models import Db, Dbxref
from machado.models import Biomaterial, Db, Dbxref
from machado.models import Cv, Cvterm
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class ProjectLoader(object):
    """Load project."""

    help = 'Load project record.'
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

    def load_project(self,
                     name:str) -> None:
        self.name = name

        try:
            self.project = Project.objects.create(name=self.name)
        except IntegrityError as e:
            raise ImportingError(e)

    def load_project_dbxref(self,
                            acc: Union[str, Dbxref],
                            is_current:bool) -> None:
        if self.project:
            # for example, acc is the "GSExxxx" sample accession from GEO
            if isinstance(acc, Dbxref):
                self.dbxref = acc
            else:
                try:
                    self.dbxref = Dbxref.objects.create(accession=acc,
                                                        db=self.db,
                                                        version=None)
                except IntegrityError as e:
                    raise ImportingError(e)
            try:
                self.project_dbxref = ProjectDbxref.objects.create(
                                           project=self.project,
                                           dbxref=self.dbxref,
                                           is_current=is_current)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            raise ImportingError(
                "Parent not found: loaded project is required to store "
                "a project_dbxref.")
