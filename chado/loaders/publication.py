"""Load publication file."""
from chado.models import Pub, Cvterm, Cv, Dbxref, Db
from chado.loaders.exceptions import ImportingError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class PublicationLoader(object):
    """Load publication records."""

    help = 'Load publication records.'

    def __init__(self, entrytype):
        """Execute the init function."""
        try:
            self.db_type, created = Db.objects.get_or_create(name='internal')
            self.dbxref_type, created = Dbxref.objects.get_or_create(
                                            accession=entrytype,
                                            db=self.db_type)
            self.cv_type, created = Cv.objects.get_or_create(name='null')
            self.cvterm_type, created = Cvterm.objects.get_or_create(
                                            name=entrytype,
                                            cv=self.cv_type,
                                            dbxref=self.dbxref_type,
                                            is_obsolete=0,
                                            is_relationshiptype=0)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_bibtex_entry(self, entry=object):
        """Store bibtex entry."""
        pub = 0
        try:
            pub = Pub.objects.create(type=self.cvterm_type,
                                     uniquename=entry['ID'],
                                     title=entry['title'],
                                     pyear=entry['year'],
                                     pages=entry['pages'],
                                     volume=entry['volume'],
                                     series_name=entry['journal'])
        except ObjectDoesNotExist as e1:
                raise ImportingError(e1)
        return pub
