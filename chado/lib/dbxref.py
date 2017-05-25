from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db, Dbxref
from chado.lib.project import get_set_project_dbxref
from chado.lib.db import get_set_db


def get_set_dbxref(db_name, accession, **kargs):

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


def get_dbxref(db_name, accession):

    # Get/Set Db instance: db
    db = Db.objects.get(name=db_name)

    try:
        # Check if the dbxref is already registered
        dbxref = Dbxref.objects.get(db=db, accession=accession)
        return dbxref
    except ObjectDoesNotExist:
        return None
