from datetime import datetime
from django.core.management.base import BaseCommand
from chado.lib.dbxref import get_set_dbxref
from chado.lib.cvterm import get_set_cv, get_set_cvterm
from chado.lib.db import set_db_file
from chado.lib.project import (get_project, get_set_project_dbxref)


class Command(BaseCommand):
    help = 'Load cvterms for NCBI\'s taxonomy file. To see the terms, run the'
    'following shell command:'
    'awk \'BEGIN{FS="\t\|\t"}{print $3}\' taxdump/nodes.dmp | sort -u '

    data = ["class", "cohort", "family", "forma", "genus", "infraclass",
            "infraorder", "kingdom", "no rank", "order", "parvorder",
            "phylum", "species", "species group", "species subgroup",
            "subclass", "subfamily", "subgenus", "subkingdom", "suborder",
            "subphylum", "subspecies", "subtribe", "superclass", "superfamily",
            "superkingdom", "superorder", "superphylum", "tribe", "varietas"]

    db_name = 'species_taxonomy'
    cv_name = 'taxonomy'

    def add_arguments(self, parser):
        parser.add_argument("--description", help="DB Description",
                            required=True, type=str)
        parser.add_argument("--update", help="Overwrite existing sequences",
                            required=False, action='store_true')
        parser.add_argument("--project", help="Project name", required=False,
                            type=str)

    def handle(self, *args, **options):
        # retrieve project object
        project = ""
        if options['project']:
            project_name = options['project']
            project = get_project(project_name)

        # get db object
        # this should use the function get_set_db, in dbxref lib but
        # that does not have the 'description' field to be inserted.
        # using set_db_file instead.
        db = set_db_file(file=self.db_name,
                         description=options['description'])
        # get cv object
        cv = get_set_cv(self.cv_name)

        for taxa in self.data:
                # get dbxref object
                accession = "taxonomy:" + taxa
                print("inserting taxa: %s ; accession is: %s"
                      % (taxa, accession))

                dbxref = get_set_dbxref(db_name=db.name,
                                        accession=accession,
                                        description=taxa)

                # get cvterm object
                get_set_cvterm(cv_name=cv.name,
                               cvterm_name=taxa,
                               definition=cv.name,
                               dbxref=dbxref,
                               is_relationshiptype=0)

                if project:
                        get_set_project_dbxref(dbxref=dbxref, project=project)

        self.stdout.write(self.style.SUCCESS('%s Done. '
                                             % (datetime.now())))
