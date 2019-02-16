Loading FASTA files
===================

Load FASTA
----------

.. code-block:: bash

    python manage.py load_fasta --file organism_chrs.fa --soterm chromosome --organism 'Arabidopsis thaliana'

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_fasta --help

=============   ==================================================================================
--file 			FASTA File *
--organism 		Species name (eg. Homo sapiens, Mus musculus) *
--soterm 		SO Sequence Ontology Term (eg. chromosome, assembly) *
--description	Description
--url 			URL
--doi 			DOI of a reference stored using *load_publication* (eg. 10.1111/s12122-012-1313-4)
--nosequence    Don't load the sequences
--cpu 			Number of threads
=============   ==================================================================================

\* required fields


Remove file
-----------

If, by any reason, you need to remove a fasta dataset you should use the command *remove_file*. **If you delete a file, every record that depend on it will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_file --help

* This command requires the file name (Dbxrefprop.value)
