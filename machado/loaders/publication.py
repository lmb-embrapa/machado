# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load publication file."""
import re

from machado.models import Pub, PubDbxref, Pubauthor, Cvterm, Cv, Dbxref, Db


class PublicationLoader(object):
    """Load publication records."""

    help = "Load publication records."

    def store_bibtex_entry(self, entry: dict):
        """Store bibtex entry."""
        db_type, created = Db.objects.get_or_create(name="internal")
        cv_type, created = Cv.objects.get_or_create(name="null")
        dbxref_type, created = Dbxref.objects.get_or_create(
            accession=entry["ENTRYTYPE"], db=db_type
        )
        cvterm_type, created = Cvterm.objects.get_or_create(
            name=entry["ENTRYTYPE"],
            cv=cv_type,
            dbxref=dbxref_type,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        title = entry.get("title")
        title = re.sub("^{", "", title)
        title = re.sub("}$", "", title)

        pub = Pub.objects.create(
            type=cvterm_type,
            uniquename=entry.get("ID"),
            title=title,
            pyear=entry.get("year"),
            pages=entry.get("pages"),
            volume=entry.get("volume"),
            series_name=entry.get("journal"),
        )
        # try to store DOI information
        if pub and (("doi" in entry) or ("DOI" in entry)):
            db_doi, created = Db.objects.get_or_create(name="DOI")
            try:
                doi = entry["DOI"]
            except KeyError:
                doi = entry["doi"]
            dbxref_doi, created = Dbxref.objects.get_or_create(accession=doi, db=db_doi)
            PubDbxref.objects.create(pub=pub, dbxref=dbxref_doi, is_current=True)
        # try to store author information
        if pub and (("author" in entry) or ("AUTHOR" in entry)):
            author_line = ""
            if "author" in entry:
                author_line = entry["author"]
            elif "AUTHOR" in entry:
                author_line = entry["AUTHOR"]

            # retrieve every givenname and surname and create tables
            # for them (authors are separated by "and"; surnames and
            # names are separated by ",".
            authors = author_line.split("and")

            # enumerate returns author ranks automagically
            for rank, author in enumerate(authors):
                names = author.split(",")
                surname = names[0].strip()
                givennames = ""
                if len(names) > 1:
                    givennames = names[1].strip()
                pubauthor, created = Pubauthor.objects.get_or_create(
                    pub=pub, rank=rank, surname=surname, givennames=givennames
                )
