import os
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Db, Dbprop


def get_set_db(db_name, **kargs):
    description = kargs.get('description')
    urlprefix = kargs.get('urlprefix')
    url = kargs.get('url')

    try:
        # Check if the db is already registered
        db = Db.objects.get(name=db_name)
        return db

    except ObjectDoesNotExist:

        # Save the name to the Db model
        db = Db.objects.create(name=db_name,
                               description=description,
                               urlprefix=urlprefix,
                               url=url)
        db.save()
        return db


def set_db_file(file, **args):
    try:
        file = os.path.basename(file)
        db = Db.objects.get(name=file)
        if db is not None:
            raise IntegrityError('The db %s is already registered.'
                                 % db.name)
    except ObjectDoesNotExist:
        db = Db.objects.create(name=file,
                               description=args.get('description'),
                               url=args.get('url'))
    return db


def get_set_dbprop(db, cvterm_id, value, rank=0):

    dbprop = ""

    try:
        # Check if the dbxref is already registered
        dbprop = Dbprop.objects.get(db=db, type_id=cvterm_id)

    except ObjectDoesNotExist:

        # Save to the Dbxref model
        dbprop = Dbprop.objects.create(db=db,
                                       type_id=cvterm_id,
                                       value=value,
                                       rank=rank)
        dbprop.save()
    return dbprop
