Loading Coexpression analyzes
=============================

Load Coexpression correlated pairs of features
----------------------------------------------
Coexpression analyzes usually generate correlation statistics regarding gene sets in a pairwise manner.
For example, LSTrAP can generate a table with the Pearson correlation coefficient for every pair of genes in
a RNA-seq experiment.

To load such a table into Machado, the file must be headless and tab separated, with the two first columns
containing the correlated pair of IDs for the genes/features and the third column must contain the correlation
coefficient among them. In the case of the output of the LSTrAP software, the coefficient is subtracted by 0.7
for normalization sakes.

A one line sample from such a table is showed below:

.. code-block:: bash

    AT2G44195.1.TAIR10      AT1G30080.1.TAIR10      0.18189286870895194
    AT2G44195.1.TAIR10      AT5G24750.1.TAIR10      0.1715779378273995

Note: The feature pairs from columns 1 and 2 need to be loaded previously.

To load such a table, one can run the command below:

.. code-block:: bash

    python manage.py load_coexpression_pairs --file pcc.mcl.txt

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_coexpression_pairs --help

=============   ==================================================================================
--file           'pcc.mcl.txt' File *
--soterm         'mRNA' sequence ontology term *default*
--cpu 	          Number of threads
=============   ==================================================================================

\* example output file from LSTrAP software.

Remove coexpression pairs
-------------------------

If, by any reason, you need to remove coexpression pair analyzes, all you need to do is pass
the filename used to load the analyzes to the remove_relationships command: remove_relationship --file <coexpression_file>'
**Every coexpression relations from coexpression_file (e.g. 'pcc.mcl.txt' from LSTrAP) will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_relationship --help

=============   ==================================================================================
--file           'mcl.clusters.txt' file *
=============   ==================================================================================

\* example output file from LSTrAP software.


Load Coexpression clusters
---------------------------

Other type of coexpression analyzes involve clustering features using its correlation values.
LSTrAP does that using the 'mcl' software. To load data from such analyzes, the input file must be
headless and fields tab separated, with each line representing one cluster, and each column representing
one gene/feature from that cluster. The first column should represent the cluster name and must have the
format: "<cluster_name>:".
Three-cluster sample from such a file is shown below, the first line
represents a cluster with three individuals, the second line a cluster with two, and the third line an
orphaned cluster with only one individual (obs: orphaned clusters are discarded).:

.. code-block:: bash

    ath_1:    AT3G18715.1.TAIR10      AT3G08790.1.TAIR10      AT5G42230.1.TAIR10
    ath_2:    AT1G27040.1.TAIR10      AT1G71692.1.TAIR10
    ath_3:    AT5G24750.1.TAIR10

Note: The genes/features from each column must be loaded previously.

To load such a file, one can run the command below:

.. code-block:: bash

    python manage.py load_coexpression_clusters --file mcl.clusters.txt --organism 'Arabidopsis thaliana'

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_coexpression_clusters --help

=============   ==================================================================================
--file           'mcl.clusters.txt' file *
--organism        Scientific name (e.g.: 'Arabidopsis thaliana')
--soterm         'mRNA' sequence ontology term *default*
--cpu 	          Number of threads
=============   ==================================================================================

\* example output file from LSTrAP software.

Remove coexpression clusters
----------------------------

If, by any reason, you need to remove coexpression cluster analyzes, you need to pass
the controlled vocabulary term 'coexpression group' and the organism scientific name to
the command remove_feature_group: *remove_feature_group --cvterm 'coexpression group' --organism 'Arabidopsis thaliana'* *

\*Every coexpression group relations from that organism will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_feature_annotation --help

====================  ========================================
--cvterm TERM            mandatory: 'coexpression group'
--organism ORGANISM    Scientific name (e.g.: 'Oryza sativa')
====================  ========================================
