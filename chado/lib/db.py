import os
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Db


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
