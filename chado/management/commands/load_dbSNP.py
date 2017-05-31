from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from chado.lib.dbxref import get_set_dbxref
from chado.lib.db import set_db_file, get_set_db, get_set_dbprop
from chado.lib.cvterm import get_set_cv, get_set_cvterm, get_set_cvtermprop
from chado.lib.organism import get_set_organism
from chado.lib.project import (get_project)
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Feature, Featureprop
from pysam import VariantFile


class Command(BaseCommand):
    help = 'Load NCBIs dbSNP VCF file (use tabix to index file is suggested). '
    'Following VCF specifications from: https://samtools.github.io/hts-specs/'

    cv_name = 'feature_property'
    db_name = 'VCF'
    db_description = 'Variant Call Format'
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
        parser.add_argument("--organism", help="organism scientific name"
                            " (Genus species)", required=True, type=str)
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--project", help="Project name", required=False,
                            type=str)

    def handle(self, *args, **options):
        # retrieve project object
        project = ""
        if options['project']:
            project_name = options['project']
            project = get_project(project_name)

        # create cv object
        cv = get_set_cv(cv_name=self.cv_name)
        db_cv = get_set_db(db_name=self.db_name,
                           description=self.db_description)

        # get organism object
        organism = get_set_organism(options['organism'])

        # get db object
        db_file = set_db_file(file=options['vcf'],
                              description=options.get('description'))

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
        self.stdout.write('%s Processing header...' % datetime.now())
        for x in vcf_in.header.records:
            # GENERIC are cvterms for the DB file
            if (x.type in ["GENERIC"]):
                dbxref_file = get_set_dbxref(db_name=db_file.name,
                                             # e.g. "RSPOS"
                                             accession=x.value,
                                             # e.g. "GENERIC"
                                             version=x.type,
                                             # e.g. "dbSNP_BUILD_ID"
                                             description=x.key)

                cvterm_file = get_set_cvterm(cv_name=cv.name,
                                             cvterm_name=x.key,
                                             definition=x.value,
                                             dbxref=dbxref_file,
                                             is_relationshiptype=0)

                get_set_dbprop(db=db_file,
                               cvterm_id=cvterm_file.cvterm_id,
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
                            dbxref = get_set_dbxref(db_name=db_cv.name,
                                                    # x["ID"] or "RSPOS"
                                                    accession=tup[1],
                                                    # e.g. "FORMAT"
                                                    version=x.type,
                                                    # e.g. "ID"
                                                    description=tup[0])
                            cvterm = get_set_cvterm(cv_name=cv.name,
                                                    # e.g. "RSPOS"
                                                    cvterm_name=tup[1],
                                                    # e.g. "INFO"
                                                    definition=tup[0],
                                                    dbxref=dbxref,
                                                    is_relationshiptype=0)
                            get_set_cvtermprop(cvterm=cvterm,
                                               type_id=cvterm.cvterm_id,
                                               # e.g. "1"
                                               value=x.type,
                                               rank=0)
                        else:
                            # create dbxref and cvterm objects for the
                            # property information of the ID terms
                            # e.g. Number, Type...
                            dbxref_sub = get_set_dbxref(db_name=db_cv.name,
                                                        # e.g. "Number"
                                                        accession=tup[0],
                                                        # "INFO"
                                                        version=x.type,
                                                        description=tup[0])
                            cvterm_sub = get_set_cvterm(cv_name=cv.name,
                                                        # e.g. "Number"
                                                        cvterm_name=tup[0],
                                                        # e.g. "RSPOS"
                                                        definition=cvterm.name,
                                                        dbxref=dbxref_sub,
                                                        is_relationshiptype=0)
                            get_set_cvtermprop(cvterm=cvterm,
                                               type_id=cvterm_sub.cvterm_id,
                                               # e.g. "1"
                                               value=tup[1],
                                               rank=0)
        # start storing data from the record field
        # first, get/set the cvterms for the mandatory 8 fields of the header
        for tuples in self.header_fields:
            # print(tuples)
            # print(VCF_version.value)
            dbxref_header = get_set_dbxref(db_name=db_cv.name,
                                           # e.g. "RSPOS"
                                           accession=tuples[0],
                                           # e.g. "GENERIC"
                                           version=VCF_version.value,
                                           # e.g. "dbSNP_BUILD_ID"
                                           description=tuples[1])

            get_set_cvterm(cv_name=cv.name,
                           cvterm_name=tuples[0],
                           definition=tuples[1],
                           dbxref=dbxref_header,
                           is_relationshiptype=0)

        counter = 0
        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
        # start iterating through record data fields to store features
        self.stdout.write('%s Processing records...' % datetime.now())
        for rec in vcf_in.fetch():

            # simple counter status
            counter += 1
            if not counter % 1000:
                self.stdout.write('%s - %s features processed.'
                                  % (datetime.now(), counter))

            fields = str(rec).split()
            # get/set dbxref for SNP ID
            dbxref_rec = get_set_dbxref(db_name=db_file.name,
                                        accession=fields[2],
                                        project=project)
            # retrieve cvterm "ID"
            cvterm_rec = get_set_cvterm(cv_name=cv.name,
                                        cvterm_name="ID",
                                        dbxref=dbxref_rec)
            # creating a new feature
            feature_rec = Feature.objects.create(dbxref=dbxref_rec,
                                                 organism=organism,
                                                 name=fields[2],
                                                 uniquename=fields[2],
                                                 type_id=cvterm_rec.cvterm_id,
                                                 is_analysis=False,
                                                 is_obsolete=False,
                                                 timeaccessioned=datetime.
                                                 now(timezone.utc),
                                                 timelastmodified=datetime.
                                                 now(timezone.utc)
                                                 )
            # load feature properties (do not need 2 (ID). 7 (INFO) will be
            # parsed later on...
            for i in range(7):
                # retrieve cvterm
                # print(self.header_fields[i][0])
                cvterm_field = get_set_cvterm(
                        cv_name=cv.name,
                        cvterm_name=self.header_fields[i][0],
                        dbxref=dbxref_rec
                        )
                Featureprop.objects.create(
                              feature=feature_rec,
                              type_id=cvterm_field.cvterm_id,
                              value=fields[i],
                              rank=0
                              )
            # parse 8th field (INFO) and load feature properties
            # print(fields[7])
            info_fields = fields[7].split(";")
            # print(info_fields)
            for field in info_fields:
                # print(field)
                key_value = field.split("=")
                if len(key_value) == 1:
                    key_value.append("0")
                # print(key_value)
                cvterm_info = get_set_cvterm(cv_name=cv.name,
                                             cvterm_name=key_value[0],
                                             dbxref=dbxref_rec
                                             )
                Featureprop.objects.create(
                                           feature=feature_rec,
                                           type_id=cvterm_info.cvterm_id,
                                           value=key_value[1],
                                           rank=0
                                           )

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
