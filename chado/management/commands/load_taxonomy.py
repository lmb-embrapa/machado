from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from chado.lib.dbxref import get_set_dbxref
from chado.lib.db import set_db_file
from chado.lib.organism import get_set_organism, get_set_organism_dbxref
from chado.lib.project import (get_project, get_set_project_dbxref)
import re
import sys


class Command(BaseCommand):
    help = 'Load NCBI\'s taxonomy file'

    def add_arguments(self, parser):
        parser.add_argument("--names", help="names file", required=True,
                            type=str)
        parser.add_argument("--nodes", help="node file <NOT IMPLEMENTED YET",
                            required=False,
                            type=str)
        parser.add_argument("--description", help="DB Description",
                            required=True, type=str)
        parser.add_argument("--url", help="DB URL", required=True, type=str)
        parser.add_argument("--update", help="Overwrite existing sequences",
                            required=False, action='store_true')
        parser.add_argument("--project", help="Project name", required=False,
                            type=str)

    # description field example:
    # 'description='gi|1003052167|emb|CZF77396.1| 2-succinyl-6-hydroxy-2,
    # 4-cyclohexadiene-1-carboxylate synthase [Grimontia marina]'''
    def parse_scientific_name(self, scname):
        # print("# desc field: %s" % first_fasta_description_field)
        fields = scname.split(" ")
        # print("1st field: %s" % fields[0])
        # print("2nd field: %s" % fields[1])
        # print("fields: %s" % fields.group(0))
        # name_fields = fields.group(0).split(" ")
        infra = ""
        genus = fields[0]
        species = ".spp"
        # special case when there is no specific name...
        if len(fields) > 1:
            species = fields[1]
            if len(fields) > 2:
                infra = scname
        # print("scientific name: %s" % (genus + " " + species))
        return((genus + " " + species), infra)

    def handle(self, *args, **options):
        # retrieve project object
        project = ""
        if options['project']:
            project_name = options['project']
            project = get_project(project_name)

        # get db object
        db = set_db_file(file=options['names'],
                         description=options['description'],
                         url=options['url'])

        # open handle for reading names.dmp file
        names_lines = ""
        try:
            names_lines = open(options['names'], 'r')
        except IOError:
            raise IOError("Error: File does not appear to exist.")
        counter = 0
        for line in names_lines:
            taxid = ""
            scname = ""
            infra = ""
            # print("line now is %s" % line)
            # parse line to get the scientific names
            fields = re.split("\s\|\s", line)
            # fields = lines.split("\t|\t")
            # print("fields %s" % fields)
            if (fields[3] == "scientific name"):
                taxid = fields[0]
                scname = fields[1]
                # print("taxid %s" % taxid)
                # print("scientific name %s" % scname)
                # sys.exit()
                # get dbxref object
                dbxref = get_set_dbxref(db.name, taxid, scname)
                # set variable for organism object
                organism_name = ""
                # parse organism genus and species names from fasta description
                # try to get or set organism
                try:
                    organism_name, infra = self.parse_scientific_name(scname)
                except:
                    raise IntegrityError('The organism name could not be '
                                         'obtained from the scname: %s'
                                         % scname)

                # create objects
                organism = get_set_organism(organism_name, infra)
                get_set_organism_dbxref(organism, dbxref)
                counter += 1
                sys.stdout.write('Scientific names inserted: %s\r' % counter)
                sys.stdout.flush()

                # create project_dbxref and project_feature
                if project:
                        get_set_project_dbxref(dbxref=dbxref, project=project)
            # else:
                # print("field %s is not scientific name" % fields[3])

        self.stdout.write(self.style.SUCCESS('%s Done. %r names inserted. '
                                             % (datetime.now(), counter)))
