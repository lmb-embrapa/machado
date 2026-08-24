# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load publication file."""

import re
import unicodedata

from machado.models import Pub, PubDbxref, Pubauthor, Cvterm, Cv, Dbxref, Db

# LaTeX macros seen in imported BibTeX titles that have no brace argument
# (e.g. "Gs$\upalpha$", "Holstein{\textendash}Friesian"); each maps to the
# plain-text symbol it renders as.
_LATEX_SYMBOL_MACROS = {
    "greater": ">",
    "mathplus": "+",
    "prime": "'",
    "textendash": "\u2013",
    "textquotesingle": "'",
    "texttimes": "\u00d7",
    "upalpha": "\u03b1",
    "upbeta": "\u03b2",
    "upmu": "\u03bc",
}

_HSPACE_RE = re.compile(r"\\hspace\{[^{}]*\}")
_BARE_MACRO_RE = re.compile(r"\\([A-Za-z]+)")
_COMMAND_BEFORE_BRACE_RE = re.compile(r"\\[A-Za-z]+(?=\{)")

# Standard LaTeX diacritic commands, e.g. "\'e" or "\'{e}" for "é". Combined
# with the target letter via Unicode combining marks and NFC-normalized into
# a single precomposed character, so this covers any accented letter rather
# than needing one dict entry per letter/accent combination.
_ACCENT_COMBINING_MARKS = {
    "'": "\u0301",  # acute
    "`": "\u0300",  # grave
    '"': "\u0308",  # diaeresis
    "^": "\u0302",  # circumflex
    "~": "\u0303",  # tilde
}
_ACCENT_RE = re.compile(r"\\(['`\"^~])\{?([a-zA-Z])\}?")


def clean_bibtex_title(title):
    """Strip BibTeX/LaTeX markup from a title for plain-text display.

    BibTeX titles wrap words in braces purely to protect capitalization
    (e.g. "{GWAS}", "{{FABP1}}") and may carry LaTeX formatting commands
    ("\\textit{{FABP1}}") or symbol macros ("\\upalpha", "\\textendash").
    None of that is meaningful once rendered as plain text, so it's removed
    rather than stored as-is.
    """
    if not title:
        return title

    text = title
    # \hspace{<length>} only inserts spacing; its argument is a dimension,
    # not text, so it must be dropped entirely rather than unwrapped.
    text = _HSPACE_RE.sub(" ", text)

    # Diacritic commands ("\'e", "Montb\'eliarde") -> precomposed accented
    # letter. Must run before the bare-macro steps below: the mark character
    # right after the backslash (', `, etc.) isn't a letter, so it wouldn't
    # match those anyway, but resolving it here keeps intent explicit.
    text = _ACCENT_RE.sub(
        lambda m: unicodedata.normalize(
            "NFC", m.group(2) + _ACCENT_COMBINING_MARKS[m.group(1)]
        ),
        text,
    )

    # Known argument-less symbol macros -> their plain-text symbol.
    text = _BARE_MACRO_RE.sub(
        lambda m: _LATEX_SYMBOL_MACROS.get(m.group(1), m.group(0)), text
    )

    # Formatting commands ("\textit{{FABP1}}") must lose their command word
    # BEFORE any brace is peeled: peeling first would leave "\textit" and
    # "FABP1" touching with nothing between them, and the catch-all below
    # would then eat both as a single backslash-word, dropping the letters
    # of the content that immediately follow (turning "KCNJ11" into "11").
    text = _COMMAND_BEFORE_BRACE_RE.sub("", text)

    # Catch-all for any remaining argument-less, unmapped backslash command.
    text = _BARE_MACRO_RE.sub("", text)

    # Every remaining brace is either a plain case-protection wrapper
    # ("{GWAS}") or -- in titles imported before this function existed --
    # an unmatched leftover from the old loader blindly stripping only the
    # string's very first "{", which orphaned the "}" of a group that
    # actually started mid-title. Either way the character itself carries
    # no display meaning, matched or not, so it's simply dropped.
    text = text.replace("{", "").replace("}", "")

    # Math-mode delimiters have no rendering meaning as plain text.
    text = text.replace("$", "")

    # BibTeX source lines are sometimes hard-wrapped mid-word; this can't
    # recover the original word, but at least turns a stray newline into a
    # space instead of a display glitch.
    text = re.sub(r"\s+", " ", text).strip()

    return text


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

        title = clean_bibtex_title(entry.get("title"))

        pub, created = Pub.objects.get_or_create(
            type=cvterm_type,
            uniquename=entry.get("ID"),
            defaults={
                "title": title,
                "pyear": entry.get("year"),
                "pages": entry.get("pages"),
                "volume": entry.get("volume"),
                "series_name": entry.get("journal"),
            },
        )
        # try to store DOI information
        if pub and (("doi" in entry) or ("DOI" in entry)):
            db_doi, created = Db.objects.get_or_create(name="DOI")
            try:
                doi = entry["DOI"]
            except KeyError:
                doi = entry["doi"]
            dbxref_doi, created = Dbxref.objects.get_or_create(
                accession=doi.lower(), db=db_doi
            )
            PubDbxref.objects.get_or_create(pub=pub, dbxref=dbxref_doi, is_current=True)
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
                    pub=pub,
                    rank=rank,
                    defaults={"surname": surname, "givennames": givennames},
                )
