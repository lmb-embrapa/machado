"""Load publication file."""
from machado.models import Pub, PubDbxref, Pubauthor, Cvterm, Cv, Dbxref, Db
from machado.loaders.exceptions import ImportingError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class PublicationLoader(object):
    """Load publication records."""

    help = 'Load publication records.'

    def __init__(self, entrytype: str) -> None:
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

    def store_bibtex_entry(self, entry: dict):
        """Store bibtex entry."""
        try:
            pub = Pub.objects.create(type=self.cvterm_type,
                                     uniquename=entry.get('ID'),
                                     title=entry.get('title'),
                                     pyear=entry.get('year'),
                                     pages=entry.get('pages'),
                                     volume=entry.get('volume'),
                                     series_name=entry.get('journal'))
            # try to store DOI information
            if (pub and (("doi" in entry) or ("DOI" in entry))):
                    self.db_doi, created = Db.objects.get_or_create(name='doi')
                    doi = ""
                    if ("doi" in entry):
                        doi = entry["doi"]
                    elif ("DOI" in entry):
                        doi = entry["DOI"]
                    self.dbxref_doi, created = Dbxref.objects.get_or_create(
                                                    accession=doi,
                                                    db=self.db_doi)
                    PubDbxref.objects.create(pub=pub,
                                             dbxref=self.dbxref_doi,
                                             is_current=True)
            # try to store author information
            if (pub and (("author" in entry) or ("AUTHOR" in entry))):
                    author_line = ""
                    if ("author" in entry):
                        author_line = entry["author"]
                    elif ("AUTHOR" in entry):
                        author_line = entry["AUTHOR"]

                    # retrieve every givenname and surname and create tables
                    # for them (authors are separated by "and"; surnames and
                    # names are separated by ",".
                    authors = author_line.split("and")

                    # enumerate returns author ranks automagically
                    for rank, author in enumerate(authors):
                        names = author.split(",")
                        surname = names[0].lstrip()
                        givennames = ""
                        if (len(names) > 1):
                            givennames = names[1].lstrip()
                        self.pubauthor, created = Pubauthor.objects.\
                            get_or_create(pub=pub,
                                          rank=rank,
                                          surname=surname,
                                          givennames=givennames)
        except ObjectDoesNotExist as e1:
                raise ImportingError(e1)
