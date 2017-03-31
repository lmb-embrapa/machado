from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Organism, Feature, Featureloc, FeatureDbxref, Dbxref, Db, Cvterm 

import gffutils
import pysam

from chado.lib.dbxref import *
from chado.lib.cvterm import *
from chado.lib.gff import *
from chado.lib.feature import *

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

class Command(BaseCommand):
    help = 'Load GFF3 genome file indexed with tabix. Example: (grep ^"#" in.gff; grep -v ^"#" in.gff | sort -k1,1 -k4,4n) | bgzip > sorted.gff.gz; tabix -p gff sorted.gff.gz; tabix sorted.gff.gz chr1:10,000,000-20,000,000; '

    def add_arguments(self, parser):
        parser.add_argument("--in", help="GFF3 genome file indexed with tabix (see http://www.htslib.org/doc/tabix.html)", required = True, type=str)
        parser.add_argument("--organism_id", help="GFF3 genome file indexed with tabix (see http://www.htslib.org/doc/tabix.html)", required = True, type=int)

    def handle(self, *args, **options):

        # Load the GFF3 file
        with open(options['in']) as tbx_file:
            #print(str(tbx_file.name))
            tbx = pysam.TabixFile(tbx_file.name)

            # check GFF for anomalies
            #for row in tbx.fetch("chrI", 1, 2000, parser=pysam.asGTF()):
            for row in tbx.fetch(parser=pysam.asGTF()):
                have_parent = check_parent(row)
                if (not have_parent):
                    # populate tables related to GFF
                    ID = get_attribute(row,"ID")
                    Contig = get_attribute(row,"ID")
                    print("ID: %s" % ID)
                else:
                    Parent = get_attribute(row,"Parent")
                    print("Parent: %s" % Parent)
                    # check relations
                       




