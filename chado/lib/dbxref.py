from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db,Dbxref


def get_set_db(name):

    try:
        # Check if the db is already registered
        db = Db.objects.get(name=name)
        return db

    except ObjectDoesNotExist:

        # Save the name to the Db model
        db = Db.objects.create(name=name)
        db.save()
        #self.stdout.write('Db: %s registered' % name)
        return db


def get_set_dbxref(db,accession,description):

    # Get/Set Db instance: db
    db = get_set_db(db)

    try:
        # Check if the dbxref is already registered
        dbxref = Dbxref.objects.get(db=db,accession=accession)
        return dbxref

    except ObjectDoesNotExist:

        # Save to the Dbxref model
        dbxref = Dbxref.objects.create(db=db,accession=accession,description=description)
        dbxref.save()
        return dbxref

