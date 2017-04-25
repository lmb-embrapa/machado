import hashlib
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Feature
from Bio import SeqIO
from chado.lib.dbxref import get_set_dbxref
from chado.lib.organism import get_set_organism
from chado.lib.db import set_db_file
from chado.lib.cvterm import get_ontology_term
import re
# import json


class Command(BaseCommand):
    help = 'Load NCBI\'s NR FASTA file'

    def add_arguments(self, parser):
        parser.add_argument("--fasta", help="FASTA File", required=True,
                            type=str)
        parser.add_argument("--description", help="DB Description",
                            required=True, type=str)
        parser.add_argument("--url", help="DB URL", required=True, type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence",
                            required=False, action='store_true')
        parser.add_argument("--update", help="Overwrite existing sequences",
                            required=False, action='store_true')

    # get binomial name of the organism from the fasta description
    # object.
    # description field example:
    # 'description='gi|1003052167|emb|CZF77396.1| 2-succinyl-6-hydroxy-2,
    # 4-cyclohexadiene-1-carboxylate synthase [Grimontia marina]'''
    def parse_organism(self, first_fasta_description_field):
        fields = re.search(r"\[(.*)\]$", first_fasta_description_field)
        name_fields = fields.group().split(" ")
        genus = re.sub(r'^\[', '', name_fields[0])
        species = ".spp"
        # special case when there is no specific name...
        if len(name_fields) > 1:
            if re.search(r'\]$', name_fields[1]):
                species = re.sub(r'\]$', '', name_fields[1])
                print("species:%s" % species)
            else:
                species = name_fields[1]
        return(genus + " " + species)

    # get first field from multiple header entries from NCBI's nr fasta file
    def parse_header(self, fasta_description):
        fields = re.split('\x01', fasta_description)
        first = fields[0]
        print("first field is %s" % (first))
        return(first)

    def handle(self, *args, **options):
        # get db object
        db = set_db_file(options['fasta'])
        # get cvterm object
        cvterm = get_ontology_term(ontology='sequence',
                                   term='protein_coding')
        # get fasta object array
        fasta_sequences = SeqIO.parse(open(options['fasta']), 'fasta')

        for fasta in fasta_sequences:
            # parse fasta.description to get the first field (see above)
            first_fasta_description = self.parse_header(fasta.description)
            # print("fasta.id: %s" % fasta.id)
            # print("fasta description: %s" % fasta.description)
            # print("first fasta description: %s" % first_fasta_description)
            # get dbxref object
            dbxref = get_set_dbxref(db.name, fasta.id, '')
            # set variable for organism object
            organism = ""
            # parse organism genus and species names from fasta description
            # try to get or set organism
            try:
                organism_name = self.parse_organism(first_fasta_description)
            except:
                raise IntegrityError('The organism could not be obtained'
                                     'from the description: %s'
                                     % first_fasta_description)
            try:
                # get feature object
                feat = Feature.objects.get(uniquename=fasta.id)
                if feat is not None:
                    if options['update']:
                        feat.delete()
                    else:
                        raise IntegrityError('The sequence %s is already '
                                             'registered.' % fasta.id)
            except ObjectDoesNotExist:
                residues = fasta.seq
                # get organism object
                organism = get_set_organism(organism_name)
                m = ""
                if options['nosequence']:
                    residues = ''
                    m = hashlib.md5(str(fasta.seq).encode()).hexdigest()

                Feature.objects.create(dbxref=dbxref,
                                       organism=organism,
                                       name=first_fasta_description,
                                       uniquename=fasta.id,
                                       residues=residues,
                                       seqlen=len(fasta.seq),
                                       md5checksum=m,
                                       type_id=cvterm.cvterm_id,
                                       is_analysis=False,
                                       is_obsolete=False,
                                       timeaccessioned=datetime.
                                       now(timezone.utc),
                                       timelastmodified=datetime.
                                       now(timezone.utc))

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
