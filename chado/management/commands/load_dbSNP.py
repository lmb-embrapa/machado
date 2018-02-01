from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from chado.loaders.common import get_ontology_term
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Feature, Featureprop, Featureloc
from chado.models import Cv, Cvterm, Cvtermprop, Db, Dbxref, Dbprop
from chado.models import Organism, Project, ProjectFeature
import os
from pysam import VariantFile


class Command(BaseCommand):
    help = """Load NCBIs dbSNP VCF file (use tabix to index file is suggested).
              Following VCF specifications from:
              https://samtools.github.io/hts-specs/"""

    cv_name = 'feature_property'
    db_name = 'VCF'
    db_description = 'Variant Call Format'
    cvterm_snp_name = 'SNP'
    cv_src_name = 'sequence'
    cvterm_chromosome_name = 'chromosome'
    # in conformity with VCF versions 4.0, 4.1, 4.2, 4.3...
    # check: https://samtools.github.io/hts-specs/VCFv4.3.pdf
    header_fields = [("CHROM", "chromosome"), ("POS", "position"),
                     ("ID", "identifier"), ("REF", "reference base(s)"),
                     ("ALT", "alternate base(s)"), ("QUAL", "quality"),
                     ("FILTER", "filter status"),
                     ("INFO", "additional information")]

    def add_arguments(self, parser):
        parser.add_argument("--vcf", help="variant .vcf file", required=True,
                            type=str)
        parser.add_argument("--fasta", help="ref. fasta file", required=True,
                            type=str)
        parser.add_argument("--organism", help="organism scientific name"
                            " (Genus species)", required=True, type=str)
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--project", help="Project name", required=False,
                            type=str)

    def get_organism(organism):
        """Retrieve organism object."""
        try:
            aux = organism.split(' ')
            genus = aux[0]
            species = 'spp.'
            infraspecific = None
            if len(aux) == 2:
                species = aux[1]
            elif len(aux) > 2:
                species = aux[1]
                infraspecific = ' '.join(aux[2:])

        except ValueError:
            raise ValueError('The organism genus and species should be '
                             'separated by a single space')

        try:
            organism = Organism.objects.get(species=species,
                                            genus=genus,
                                            infraspecific_name=infraspecific)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('%s not registered.'
                                     % organism)
        return organism

    def handle(self, *args, **options):

        # retrieve project object
        project = ""
        if options['project']:
            project_name = options['project']
            project = Project.objects.get(name=project_name)

        # create cv object
        cv, created = Cv.objects.get_or_create(name=self.cv_name)
        db_cv, created = Db.objects.get_or_create(
            name=self.db_name,
            description=self.db_description)

        # get organism object
        organism = self.get_organism(options['organism'])

        # get db object
        filename = os.path.basename(options['vcf'])
        db_file = Db.objects.create(name=filename,
                                    description=options.get('description'))

        # REFERENCE FEATURE FOR FEATURE PROP ASSIGNING...
        # try to get reference feature (fasta file)
        db_src = ""
        try:
            db_src = Db.objects.get(name=options['fasta'])
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                "Reference db (fasta file) does not exist or was not found. "
                "VCF file should have a reference fasta file assigned in the"
                " feature table.")

        # start reading VCF file, auto-detect input format
        vcf_in = VariantFile(options["vcf"])

        # VCF format version is stored in the first line of the header *ALWAYS*
        VCF_version = ""
        try:
            VCF_version = vcf_in.header.records[0]
            if not (VCF_version.key == "fileformat"):
                raise ObjectDoesNotExist(
                    "VCF is not in conformity with the default format. "
                    "First line should contain fileformat version.")
            # print(VCF_version.value)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                "VCF is not in conformity with the default format. "
                "First line should contain fileformat version.")

        # ############################################
        # get fileformat and start storing header info
        # ############################################
        dict_cvterms_info = {}
        self.stdout.write('%s Processing header...' % datetime.now())
        for x in vcf_in.header.records:
            # GENERIC are cvterms for the DB file
            if (x.type in ["GENERIC"]):
                db, created = Db.objects.get_or_create(db=db_file.name)
                dbxref_file, created = Dbxref.objects.get_or_create(
                    db=db,
                    # e.g. "RSPOS"
                    accession=x.value,
                    # e.g. "GENERIC"
                    version=x.type,
                    # e.g. "dbSNP_BUILD_ID"
                    description=x.key)

                cv, created = Cv.objects.get_or_create(name=cv.name)
                cvterm_file, created = Cvterm.objets.get_or_create(
                    cv=cv,
                    name=x.key,
                    definition=x.value,
                    dbxref=dbxref_file,
                    is_relationshiptype=0)

                Dbprop.objects.get_or_create(db=db_file,
                                             type_id=cvterm_file.cvterm_id,
                                             value=x.type,
                                             rank=0)
            # FILTER, INFO, FORMAT, etc., are global cvterms for the
            # VCF format
            else:
                dbxref = None
                # items are tuples
                for tup in x.items():
                    if(tup[0] == "IDX"):
                        dbxref = None
                    else:
                        # create dbxref and cvterm objects for the
                        # ID terms found in FILTER, INFO and FORMAT
                        # e.g. RSPOS, RV, VP...
                        if(tup[0] == "ID"):
                            db, created = Db.objects.get_or_create(db_cv.name)
                            dbxref, created = Dbxref.objects.get_or_create(
                                db=db,
                                # x["ID"] or "RSPOS"
                                accession=tup[1],
                                # e.g. "FORMAT"
                                version=x.type,
                                # e.g. "ID"
                                description=tup[0])
                            cv, created = Cv.objects.get_or_create(
                                name=self.cv_name)
                            cvterm = Cvterm.objects.get_or_create(
                                cv=cv,
                                # e.g. "RSPOS"
                                name=tup[1],
                                # e.g. "INFO"
                                definition=tup[0],
                                dbxref=dbxref,
                                is_obsolete=0,
                                is_relationshiptype=0)
                            Cvtermprop.objects.get_or_create(
                                cvterm=cvterm,
                                type_id=cvterm.cvterm_id,
                                # e.g. "1"
                                value=x.type,
                                rank=0)
                            # store cvterm for further use
                            dict_cvterms_info[tup[1]] = cvterm
                        else:
                            # create dbxref and cvterm objects for the
                            # property information of the ID terms
                            # e.g. Number, Type...
                            db, created = Db.objects.get_or_create(db_cv.name)
                            dbxref_sub, created = Dbxref.objects.get_or_create(
                                db=db,
                                # e.g. "Number"
                                accession=tup[0],
                                # "INFO"
                                version=x.type,
                                description=tup[0])
                            cv_sub, created = Cv.objects.get_or_create(
                                name=cv.name)
                            cvterm_sub, created = Cvterm.objects.get_or_create(
                                cv=cv_sub,
                                # e.g. "Number"
                                name=tup[0],
                                # e.g. "RSPOS"
                                definition=cvterm.name,
                                dbxref=dbxref_sub,
                                is_obsolete=0,
                                is_relationshiptype=0)
                            Cvtermprop.objects.get_or_create(
                                cvterm=cvterm,
                                type_id=cvterm_sub.cvterm_id,
                                # e.g. "1"
                                value=tup[1],
                                rank=0)
        # start storing data from the record field
        # first, get/set the cvterms for the mandatory 8 fields of the header
        # create dictionary of header objects for further reuse
        dict_header_cvterms = {}
        for tuples in self.header_fields:
            # print(tuples)
            # print(VCF_version.value)
            db, created = Db.objects.get_or_create(db_cv.name)
            dbxref_header, created = Dbxref.objects.get_or_create(
                db=db,
                # e.g. "POS"
                accession=tuples[0],
                # e.g. "VCF4.0"
                version=VCF_version.value,
                # e.g. "position"
                description=tuples[1])

            cv_header, created = Cv.objects.get_or_create(
                name=cv.name)
            cvterm_header, created = Cvterm.objects.get_or_create(
                cv=cv_header,
                name=tuples[0],
                definition=tuples[1],
                dbxref=dbxref_header,
                is_obsolete=0,
                is_relationshiptype=0)
            # set dictionary of cvterm objects
            dict_header_cvterms[tuples[0]] = cvterm_header

        counter = 0
        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
        dbxref_src = None
        feature_src = None
        # retrieve cvterm for SNP (sequence ontology)
        cvterm_src = get_ontology_term(ontology='sequence', term='SNP')
        # start iterating through record data fields to store features
        self.stdout.write('%s Processing records...' % datetime.now())
        for rec in vcf_in.fetch():

            # will create a list of objects for bulk creating later on
            feature_prop_list = list()

            # simple counter status
            counter += 1
            if not counter % 1000:
                self.stdout.write('%s - %s features processed.'
                                  % (datetime.now(), counter))
            # split record line in fields separated by spaces
            fields = str(rec).split()

            # get dbxref_src for featureprop assignment
            # (retrieve the 'chromosome number' feature associated to the SNP)
            if (not dbxref_src):
                dbxref_src = Dbxref.objects.get(db_id=db_src,
                                                accession=fields[0])
            # set feature_scr object ('chromosome number')
            if (not feature_src):
                feature_src = Feature.objects.get(dbxref=dbxref_src,
                                                  uniquename=fields[0])

            # get/set dbxref for SNP ID
            db, created = Db.objects.get_or_create(db=db_file.name)
            dbxref_rec, created = Dbxref.objects.get_or_create(
                db=db, accession=fields[2], project=project)
            # creating a new SNP ID feature
            feature_rec = Feature.objects.create(dbxref=dbxref_rec,
                                                 organism=organism,
                                                 name=fields[2],
                                                 uniquename=fields[2],
                                                 type_id=cvterm_src.cvterm_id,
                                                 is_analysis=False,
                                                 is_obsolete=False,
                                                 timeaccessioned=datetime.
                                                 now(timezone.utc),
                                                 timelastmodified=datetime.
                                                 now(timezone.utc)
                                                 )
            if project:
                ProjectFeature.objects.create(feature=feature_rec,
                                              project=project)
            # set position of the SNP
            Featureloc.objects.create(
                                      feature=feature_rec,
                                      srcfeature_id=feature_src.feature_id,
                                      fmin=fields[1],
                                      is_fmin_partial=False,
                                      fmax=fields[1],
                                      is_fmax_partial=False,
                                      strand=0,
                                      phase=0,
                                      locgroup=0,
                                      rank=0)
            feature_prop_list.append(
                    Featureprop(
                          feature=feature_rec,
                          type_id=dict_header_cvterms['REF'].cvterm_id,
                          value=fields[3],
                          rank=0
                    )
            )
            feature_prop_list.append(
                    Featureprop(
                          feature=feature_rec,
                          type_id=dict_header_cvterms['ALT'].cvterm_id,
                          value=fields[4],
                          rank=0
                    )
            )
            feature_prop_list.append(
                    Featureprop(
                          feature=feature_rec,
                          type_id=dict_header_cvterms['QUAL'].cvterm_id,
                          value=fields[5],
                          rank=0
                    )
            )
            feature_prop_list.append(
                    Featureprop(
                          feature=feature_rec,
                          type_id=dict_header_cvterms['FILTER'].cvterm_id,
                          value=fields[6],
                          rank=0
                    )
            )
            # start parsing INFO field
            info_fields = fields[7].split(";")
            # print(info_fields)
            for field in info_fields:
                # print(field)
                key_value = field.split("=")
                if len(key_value) == 1:
                    key_value.append("0")
                feature_prop_list.append(
                        Featureprop(
                             feature=feature_rec,
                             type_id=dict_cvterms_info[key_value[0]].cvterm_id,
                             value=key_value[1],
                             rank=0
                             )
                        )

            # bulk_create features...will try inside loop first
            Featureprop.objects.bulk_create(feature_prop_list)

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
