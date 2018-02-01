from datetime import datetime
from django.core.management.base import BaseCommand
from chado.models import Cv, Cvterm, Db, Dbxref, Project, ProjectDbxref
import re


class Command(BaseCommand):
    help = 'Load cvterms for NCBI\'s taxonomy nodes.dmp file.'
    # ranks hardcoded into 'data' array,  for *viewing* only.
    # Ranks will be retrieved from nodes.dmp file.
    # ' To see the terms, run the following shell command:'
    # ' awk \'BEGIN{FS="\t\|\t"}{print $3}\' taxdump/nodes.dmp | sort -u '
    data = ["class", "cohort", "family", "forma", "genus", "infraclass",
            "infraorder", "kingdom", "no rank", "order", "parvorder",
            "phylum", "species", "species group", "species subgroup",
            "subclass", "subfamily", "subgenus", "subkingdom", "suborder",
            "subphylum", "subspecies", "subtribe", "superclass", "superfamily",
            "superkingdom", "superorder", "superphylum", "tribe", "varietas"]

    db_name = 'species_taxonomy'
    cv_name = 'taxonomy'

    def get_ontologies_from_node_file(self, nodefile):
        # will get all ontologies from nodes.dmp file
        # dictionary
        ontologies = {}
        # open handle for reading nodes.dmp file
        lines = ""
        try:
            lines = open(nodefile, 'r')
        except IOError:
            raise IOError("Error: File does not appear to exist.")
        for line in lines:
            fields = re.split("\s+\|\s+", line)
            ontologies[fields[2]] = 1
        return ontologies

    def add_arguments(self, parser):
        parser.add_argument("--description", help="DB Description",
                            required=True, type=str)
        parser.add_argument("--file", help="nodes.dmp file", required=True,
                            type=str)
        parser.add_argument("--project", help="Project name", required=False,
                            type=str)

    def handle(self, *args, **options):
        # retrieve project object
        project = ""
        if options['project']:
            project_name = options['project']
            project = Project.objects.get(name=project_name)

        # get db object
        db, created = Db.objects.get_or_create(
            name=self.db_name,
            description=options['description'])
        # get cv object
        cv, created = Cv.objects.get_or_create(name=self.cv_name)
        ontologies = self.get_ontologies_from_node_file(options["file"])

        for rank in ontologies:
            accession = "taxonomy:" + rank
            print("inserting rank: %s ; accession is: %s"
                  % (rank, accession))

            # get dbxref object
            db, created = Db.objects.get_or_create(db=db.name)
            dbxref, created = Dbxref.objects.get_or_create(
                db=db, accession=accession, description=rank)

            # set cvterm object
            cv, created = Cv.objects.get_or_create(name=cv.name)
            Cvterm.objects.get_or_create(cv=cv,
                                         name=rank,
                                         definition=cv.name,
                                         dbxref=dbxref,
                                         is_obsolete=0,
                                         is_relationshiptype=0)

            if project:
                ProjectDbxref.objects.create(dbxref=dbxref, project=project)

        self.stdout.write(self.style.SUCCESS('%s Done. '
                                             % (datetime.now())))
