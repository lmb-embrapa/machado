"""db library."""
from cachetools import cached
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db, Dbprop
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
    except ObjectDoesNotExist:
        return None


@cached(cache={})
def get_set_dbprop(db, type_id, **kwargs):
    """Create/Retrieve dbprop object."""
    rank = kwargs.get('rank')
    value = kwargs.get('value')
    try:
        # Check if the dbprop is already registered
        dbprop = Dbprop.objects.get(db=db,
                                    type_id=type_id)

    except ObjectDoesNotExist:
        if not rank:
            rank = 0
        # Save to the Dbprop model
        dbprop = Dbprop.objects.create(db=db,
                                       type_id=type_id,
                                       value=value,
                                       rank=rank)
        dbprop.save()
    return dbprop
