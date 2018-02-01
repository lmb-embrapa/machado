"""Load NR file."""
import hashlib
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Db, Dbxref, Feature, FeatureDbxref, Organism
from Bio import SeqIO
from chado.loaders.common import get_ontology_term
import os
import re
# import json


class Command(BaseCommand):
    """Load NR file."""

    help = 'Load NCBI\'s NR FASTA file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--fasta", help="FASTA File", required=True,
                            type=str)
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence",
                            required=False, action='store_true')

    # get binomial name of the organism from the fasta description
    # object.
    # description field example:
    # 'description='gi|1003052167|emb|CZF77396.1| 2-succinyl-6-hydroxy-2,
    # 4-cyclohexadiene-1-carboxylate synthase [Grimontia marina]'''
    def parse_organism(self, description_field):
        """Parse organism name."""
        if not re.search(r'\]', description_field):
            return 'Unspecified organism', 'Unspecified organism'

        fields = re.findall(r"\[.*?\]", description_field)
        name_fields = fields[-1].split(" ")
        genus = re.sub(r'\]|\[', '', name_fields[0])

        species = ".spp"
        infra = ""
        # special case when there is no specific name...
        if len(name_fields) > 1:
            if re.search(r'\]', name_fields[1]):
                species = re.sub(r'\]', '', name_fields[1])
            else:
                species = name_fields[1]
            if len(name_fields) > 2:
                infra = genus + " " + species + " " + " ".join(name_fields[2:])
                infra = re.sub(r'\]$', '', infra)

        return(genus, species, infra)

    # get first field from multiple header entries from NCBI's nr fasta file
    def parse_header(self, fasta_description):
        """Parse fasta description."""
        fields = re.split('\x01', fasta_description)

        # trying to return the first description that contains [
        first_id_string = None
        first_desc = None
        for field in fields:
            m = re.match(r'^(\S+)\s(.+)$', fields[0])
            id_string, desc = m.group(1), m.group(2)

            # storing the first fasta_description
            if first_id_string is None:
                first_id_string, first_desc = id_string, desc

            # warning if string is too long
            if len(desc) > 255:
                print('Truncating long string: %s %s' % (id_string, desc))

            if re.search(r'\]', field):
                return id_string, desc[:255]

        # returning the first one since none have [
        return first_id_string, first_desc[:255]

    def process_id_string(self, db, id_string):
        """Process id from string."""
        # get or create dbxref for each ID separated by | and use the
        # first ID as uniquename and db,dbxref
        aux_list = id_string.split('|')
        aux_dbxrefs = zip(aux_list[::2], aux_list[1::2])

        uniquename = None
        dbxref = None
        dbxrefs = list()
        for aux_dbxref in aux_dbxrefs:
            aux_db, aux_id = aux_dbxref
            if aux_db is None:
                continue
            # print('%s %s' % (aux_db, aux_id))
            # store the first unique_name and dbxref
            if uniquename is None:
                uniquename = aux_id
                db, created = Db.objects.get_or_create(name=db.name)
                dbxref, created = Dbxref.objects.get_or_create(
                    db=db, accession=aux_id)
            # store dbxrefs for create featuredbxrefs later
            db, created = Db.objects.get_or_create(name=db.name)
            dbxref, created = Dbxref.objects.get_or_create(
                db=db, accession=aux_id)
            dbxrefs.append(dbxref)

        return uniquename, dbxref, dbxrefs

    def handle(self, *args, **options):
        """Execute the main function."""
        # get db object
        filename = os.path.basename(options['fasta'])
        db = Db.objects.create(name=filename,
                               description=options.get('description'),
                               url=options.get('url'))

        # get cvterm object
        cvterm = get_ontology_term(ontology='sequence',
                                   term='protein_coding')

        # get fasta object array
        fasta_sequences = SeqIO.parse(open(options['fasta']), 'fasta')

        counter = 0
        for fasta in fasta_sequences:
            # simple counter status
            counter += 1
            if not counter % 1000:
                self.stdout.write('%s - %s sequences processed.'
                                  % (datetime.now(), counter))

            # parse fasta.description to get the first field (see above)
            id_string, description = self.parse_header(fasta.description)

            uniquename, dbxref, dbxrefs = self.process_id_string(db, id_string)

            try:
                # get feature object
                feature = Feature.objects.get(uniquename=uniquename)
                if feature is not None:
                    raise IntegrityError('The sequence %s is already '
                                         'registered.' % uniquename)

            except ObjectDoesNotExist:

                # parse organism genus and species names from fasta description
                (genus, species, infra_name) = self.parse_organism(
                    description)

                # get or create organism object
                organism, created = Organism.objects.get_or_create(
                    genus=genus,
                    species=species,
                    infraspecific_name=infra_name)

                residues = fasta.seq
                m = hashlib.md5(str(fasta.seq).encode()).hexdigest()
                if options['nosequence']:
                    residues = ''

                feature = Feature.objects.create(
                    dbxref=dbxref,
                    organism=organism,
                    name=description,
                    uniquename=uniquename,
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

                # Associate feature with the first 2 dbxrefs
                # The sequence description may contain the | separator,
                # causing the parser to retrieve parts of the thescription
                # as dbxrefs
                for i in range(2):
                    FeatureDbxref.objects.create(feature=feature,
                                                 dbxref=dbxrefs[i],
                                                 is_current=1)

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
