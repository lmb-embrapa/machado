"""dbxref library."""
from cachetools import cached
from chado.models import Db, Dbxref
from chado.lib.project import get_set_project_dbxref
from chado.lib.db import get_set_db
from django.core.exceptions import ObjectDoesNotExist


@cached(cache={})
def get_set_dbxref(db_name, accession, **kargs):
    """Create/Retrieve dbxref object."""
    # Get/Set Db instance: db
    db = get_set_db(db_name)

    description = kargs.get('description')
    project = kargs.get('project')
    version = kargs.get('version')

    try:
        # Check if the dbxref is already registered
        dbxref = Dbxref.objects.get(db=db, accession=accession)
        if project:
            get_set_project_dbxref(dbxref=dbxref,
                                   project=project)
        return dbxref

    except ObjectDoesNotExist:
        if (not version):
            version = ""
        # Save to the Dbxref model
        dbxref = Dbxref.objects.create(db=db,
                                       accession=accession,
                                       description=description,
                                       version=version)

        dbxref.save()
        if project:
            get_set_project_dbxref(dbxref=dbxref,
                                   project=project)
        return dbxref


@cached(cache={})
def get_dbxref(db_name, accession):
    """Retrieve dbxref object."""
    # Get/Set Db instance: db
    db = Db.objects.get(name=db_name)

    try:
        # Check if the dbxref is already registered
        dbxref = Dbxref.objects.get(db=db, accession=accession)
        return dbxref
    except ObjectDoesNotExist:
        return None
