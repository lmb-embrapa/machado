Loading Feature Sequence Files
================================

Please notice the features must be loaded in advance.
The tool will try to locate the features by the sequence ID or an ID=value string in the sequence description.
For example, given the sequence header ">chr1 sequence ID=AC00123123", the tool will search the database by "chr1" and "AC00123123", respectively.
If the sequence was loaded previously, it will be replaced.


Load Feature Sequence
---------------------

.. code-block:: bash

    python manage.py load_feature_sequence --file Athaliana_transcripts.fasta --organism 'Arabidopsis thaliana' --soterm mRNA

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_feature_sequence --help

=============== ==========================================================================================
--file 			FASTA file. *
--organism 		Species name (eg. Homo sapiens, Mus musculus) *
--soterm SOTERM SO Sequence Ontology Term (eg. chromosome, assembly, mRNA, polypeptide) *
--cpu 			Number of threads
=============== ==========================================================================================

\* required fields


Remove Feature Sequence
-------------------------

If, by any reason, you need to remove a feature sequence you should use the command *load_feature_sequence* itself and provide a FASTA file with no sequence. For example:

.. code-block:: bash

    >chr1
    
    >chr2
    

