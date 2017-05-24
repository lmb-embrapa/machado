from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db, Dbxref
from chado.lib.project import get_set_project_dbxref


def get_set_db(db_name):

    try:
        # Check if the db is already registered
        db = Db.objects.get(name=db_name)
        return db

    except ObjectDoesNotExist:

        # Save the name to the Db model
        db = Db.objects.create(name=db_name)
        db.save()
        return db


def get_set_dbxref(db_name, accession, **kargs):

    # Get/Set Db instance: db
    db = get_set_db(db_name)

    description = kargs.get('description')
    project = kargs.get('project')

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
                                       description=description)
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
