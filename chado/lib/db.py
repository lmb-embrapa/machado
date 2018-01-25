"""db library."""
from cachetools import cached
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db, Dbprop
from django.db import IntegrityError
import os


@cached(cache={})
def get_set_db(db_name, **kargs):
    """Create/Retrieve db object."""
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


@cached(cache={})
def set_db_file(file, **args):
    """Create db object using the filename as name."""
    filename = os.path.basename(file)
    try:
        db = Db.objects.create(name=filename,
                               description=args.get('description'),
                               url=args.get('url'))
        return db
    except IntegrityError:
        raise('The db %s is already registered.' % db.name)


@cached(cache={})
def get_set_dbprop(db, **kwargs):
    """Create/Retrieve dbprop object."""
    rank = kwargs.get('rank')
    value = kwargs.get('value')
    cvterm_id = kwargs.get('cvterm_id')
    try:
        # Check if the dbprop is already registered
        dbprop = Dbprop.objects.get(db=db)

    except ObjectDoesNotExist:
        if not rank:
            rank = 0
        # Save to the Dbprop model
        dbprop = Dbprop.objects.create(db=db,
                                       type_id=cvterm_id,
                                       value=value,
                                       rank=rank)
        dbprop.save()
    return dbprop
