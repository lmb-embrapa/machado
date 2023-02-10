Loading FASTA files
===================

This command is mostly used to load the reference genome.
The reference sequences are exclusively used to feed JBrowse.

If the reference sequences are really long (>200Mbp), there may be memory issues during the loading process and JBrowse may take too long to render the tracks.
To avoid that, it's possible to use the parameter (--nosequence) and configure JBrowse to get the reference data from a FASTA file.


Load FASTA
----------

.. code-block:: bash

    python manage.py load_fasta --file organism_chrs.fa --soterm chromosome --organism 'Arabidopsis thaliana'

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_fasta --help

=============   ==================================================================================
--file 	        FASTA File *
--organism 	Species name (eg. Homo sapiens, Mus musculus) *
--soterm 	SO Sequence Ontology Term (eg. chromosome, assembly) *
--description	Description
--url 		URL
--doi 		DOI of a reference stored using *load_publication* (eg. 10.1111/s12122-012-1313-4)
--nosequence    Don't load the sequences
--cpu 		Number of threads
=============   ==================================================================================

\* required fields


Remove file
-----------

If, by any reason, you need to remove a FASTA file you should use the command remove_organism. Most data files you’ll load depend on the organism record (eg. fasta, gff, blast). **If you delete an organism, every data file you loaded that depend on it will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_organism --help

* These commands require the following info: Organism.genus and Organism.species
