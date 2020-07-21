Loading VCF files
=================

The first column of a VCF file is the reference sequence ID.
In order to load a VCF file, it's required to have a reference FASTA file loaded.


The VCF file must be indexed using `tabix <http://www.htslib.org/doc/tabix.html>`_.

Load VCF
--------

.. code-block:: bash

    python manage.py load_vcf --file organism_snv_sorted.gff3.gz --organism 'Arabidopsis thaliana'

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_gff --help


==========    ==================================================================================
--file 	      VCF genome file indexed with tabix (see http://www.htslib.org/doc/tabix.html) *
--organism 	  Species name (eg. Homo sapiens, Mus musculus) *
--doi 		  DOI of a reference stored using *load_publication* (eg. 10.1111/s12122-012-1313-4)
--cpu 		  Number of threads
==========    ==================================================================================

\* required fields


Remove file
-----------

If, by any reason, you need to remove a VCF dataset you should use the command *remove_file*. **If you delete a file, every record that depend on it will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_file --help

* This command requires the file name (Dbxrefprop.value)
