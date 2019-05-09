Loading taxonomy
================

Every data file you'll load (eg. fasta, gff, blast) must belong to an organism.
These are instructions to load the NCBI taxonomy, that contains most organisms you'll need.

**This step is optional.**
If you decide to skip this step, you should insert the organisms individually using the command *insert_organism*.

NCBI Taxonomy
-------------

Contains the names and phylogenetic lineages of more than 160,000 organisms that have molecular data in the NCBI databases.

* **URL**: https://www.ncbi.nlm.nih.gov/taxonomy
* **File**: ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz

After unpacking the file you'll have the required files.

.. code-block:: bash

    python manage.py load_organism --file names.dmp --name DB:NCBI_taxonomy
    python manage.py load_phylotree --file nodes.dmp --name 'NCBI taxonomy tree' --organismdb 'DB:NCBI_taxonomy'

* Loading these files can be faster if you increase the number of threads (--cpu).
* It will take a long time anyway (hours).

Remove taxonomy
---------------

If, by any reason, you need to remove a taxonomy you should use the command *remove_phylotree* and *remove_organisms*. Most data files you'll load depend on the organism database (eg. fasta, gff, blast). **If you delete an organism database, every data file you loaded will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_phylotree --help
    python manage.py remove_organisms --help

* These commands require the names of the databases (Db.name)
