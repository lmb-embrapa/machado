# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Project."""

from django.db.utils import IntegrityError

from machado.loaders.exceptions import ImportingError
from machado.models import Cvterm, Project, Projectprop


class ProjectLoader(object):
    """Load project."""

    help = "Load project record."

    def __init__(self) -> None:
        """Execute the init function."""
        self.cvterm_contained_in = Cvterm.objects.get(
            name="contained in", cv__name="relationship"
        )

    def store_project(self, name: str, filename: str) -> Project:
        """Store project."""
        try:
            project, created = Project.objects.get_or_create(name=name)
            self.store_projectprop(
                project=project,
                type_id=self.cvterm_contained_in.cvterm_id,
                value=filename,
            )
        except IntegrityError as e:
            raise ImportingError(e)
        return project

    def store_projectprop(
        self, project: Project, type_id: int, value: str, rank: int = 0
    ) -> None:
        """Store analysisprop."""
        try:
            projectprop, created = Projectprop.objects.get_or_create(
                project=project, type_id=type_id, value=value, rank=rank
            )
        except IntegrityError as e:
            raise ImportingError(e)
