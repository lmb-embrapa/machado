from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Organism, Db
import pysam

from chado.lib.feature import check_parent, get_attribute
from chado.lib.organism import get_organism


class Command(BaseCommand):
    help = 'Load GFF3 file indexed with tabix.'

    def add_arguments(self, parser):
        parser.add_argument("--gff",
                            help="GFF3 genome file indexed with tabix"
                            "(see http://www.htslib.org/doc/tabix.html)",
                            required=True,
                            type=str)
        parser.add_argument("--organism", help="Species name (eg. Homo "
                            "sapiens, Mus musculus)",
                            required=True,
                            type=str)
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)

    def handle(self, *args, **options):

        # Retrieve organism object
        organism = get_organism(options['organism'])

        # Save DB info
        db = set_db_file(file=options['fasta'],
                         description=options.get('description'),
                         url=options.get('url'))

        # Load the GFF3 file
        with open(options['in']) as tbx_file:
            # print(str(tbx_file.name))
            tbx = pysam.TabixFile(tbx_file.name)

            # check GFF for anomalies
            # for row in tbx.fetch("chrI", 1, 2000, parser=pysam.asGTF()):
            for row in tbx.fetch(parser=pysam.asGTF()):
                have_parent = check_parent(row)
                if (not have_parent):
                    # populate tables related to GFF
                    ID = get_attribute(row, "ID")
                    Contig = get_attribute(row, "ID")
                    print("ID: %s" % ID)
                else:
                    Parent = get_attribute(row, "Parent")
                    print("Parent: %s" % Parent)
                    # check relations

    def check_parent(gff3line):
            parent = 0
            try:
                fields = gff3line.attributes.split(";")
                for field in fields:
                    attribute = field.split("=")
                    if(attribute[0] == "Parent"):
                        parent = 1
                return parent

            except ObjectDoesNotExist:
                return parent
