# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Create database from chado default_schema.sql."""
from django.db import migrations
from machado.models import Db


class Migration(migrations.Migration):
    """Migration."""

    def update_db_urls(apps, schema_editor):
        """Update db urls."""

        db, created = Db.objects.get_or_create(name="BGD")
        db.urlprefix = "https"
        db.url = "bovinemine-v16.rnet.missouri.edu/bovinemine/keywordSearchResults.do?searchTerm="
        db.save()

        db, created = Db.objects.get_or_create(name="ensembl")
        db.urlprefix = "https"
        db.url = "www.ensembl.org/Multi/Search/Results?q="
        db.save()

        db, created = Db.objects.get_or_create(name="ENSEMBL")
        db.urlprefix = "https"
        db.url = "www.ensembl.org/Multi/Search/Results?q="
        db.save()

        db, created = Db.objects.get_or_create(name="ENSEMBLGENOMES-TR")
        db.urlprefix = "https"
        db.url = "ensemblgenomes.org/search/?query="
        db.save()

        db, created = Db.objects.get_or_create(name="GENEID")
        db.urlprefix = "https"
        db.url = "www.ncbi.nlm.nih.gov/search/all/?term="
        db.save()

        db, created = Db.objects.get_or_create(name="GENBANK")
        db.urlprefix = "https"
        db.url = "www.ncbi.nlm.nih.gov/search/all/?term="
        db.save()

        db, created = Db.objects.get_or_create(name="INTERPRO")
        db.urlprefix = "https"
        db.url = "www.ebi.ac.uk/interpro/entry/InterPro/"
        db.save()

        db, created = Db.objects.get_or_create(name="IPR")
        db.urlprefix = "https"
        db.url = "www.ebi.ac.uk/interpro/entry/InterPro/"
        db.save()

        db, created = Db.objects.get_or_create(name="KEGG")
        db.urlprefix = "https"
        db.url = "www.kegg.jp/dbget-bin/www_bfind_sub?mode=bfind&max_hit=100&dbkey=kegg&keywords="
        db.save()

        db, created = Db.objects.get_or_create(name="METACYC")
        db.urlprefix = "https"
        db.url = "metacyc.org/META/substring-search?object="
        db.save()

        db, created = Db.objects.get_or_create(name="MIRBASE")
        db.urlprefix = "https"
        db.url = "www.mirbase.org/results/?query="
        db.save()

        db, created = Db.objects.get_or_create(name="ncbi_gp")
        db.urlprefix = "https"
        db.url = "www.ncbi.nlm.nih.gov/search/all/?term="
        db.save()

        db, created = Db.objects.get_or_create(name="PDB")
        db.urlprefix = "https"
        db.url = "www.rcsb.org/structure/"
        db.save()

        db, created = Db.objects.get_or_create(name="REACTOME")
        db.urlprefix = "https"
        db.url = "reactome.org/content/detail/"
        db.save()

        db, created = Db.objects.get_or_create(name="refseq")
        db.urlprefix = "https"
        db.url = "www.ncbi.nlm.nih.gov/search/all/?term="
        db.save()

        db, created = Db.objects.get_or_create(name="REFSEQ")
        db.urlprefix = "https"
        db.url = "www.ncbi.nlm.nih.gov/search/all/?term="
        db.save()

        db, created = Db.objects.get_or_create(name="RFAM")
        db.urlprefix = "https"
        db.url = "rfam.org/search?q="
        db.save()

        db, created = Db.objects.get_or_create(name="TAXON")
        db.urlprefix = "https"
        db.url = "www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="
        db.save()

        db, created = Db.objects.get_or_create(name="UNIPROT")
        db.urlprefix = "https"
        db.url = "www.uniprot.org/uniprotkb/"
        db.save()

        db, created = Db.objects.get_or_create(name="UNIPROTKB/TREMBL")
        db.urlprefix = "https"
        db.url = "www.uniprot.org/uniprotkb/"
        db.save()

        db, created = Db.objects.get_or_create(name="UNIPROTKB/SWISS-PROT")
        db.urlprefix = "https"
        db.url = "www.uniprot.org/uniprotkb/"
        db.save()

        db, created = Db.objects.get_or_create(name="VGNC")
        db.urlprefix = "https"
        db.url = "vertebrate.genenames.org/data/gene-symbol-report/#!/vgnc_id/VGNC:"
        db.save()

    dependencies = [
        ("machado", "0001_initial"),
        ("machado", "0002_add_index"),
        ("machado", "0003_add_multispecies"),
        ("machado", "0004_create_history"),
    ]

    operations = [
        migrations.RunPython(update_db_urls),
    ]
