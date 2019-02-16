Loading ontologies
==================

The ontologies are required and must be loaded first.

Relations ontology
------------------

RO is an ontology of relations for use with biological ontologies.

* **URL**: https://github.com/oborel/obo-relations
* **File**: ro.obo

.. code-block:: bash

    python manage.py load_relations_ontology --file ro.obo

Sequence ontology
-----------------

Collect of SO Ontologies.

* **URL**: https://github.com/The-Sequence-Ontology/SO-Ontologies
* **File**: so.obo

.. code-block:: bash

    python manage.py load_sequence_ontology --file so.obo


Gene ontology
-------------

Source ontology files for the Gene Ontology.

* **URL**: http://current.geneontology.org/ontology/
* **File**: go.obo

.. code-block:: bash

    python manage.py load_gene_ontology --file go.obo

* Loading the gene ontology can be faster if you increase the number of threads (--cpu).
* After loading the gene ontology the following records will be created in the Cv table: gene_ontology, external, molecular_function, cellular_component, and biological_process.


Remove ontology
---------------

If, by any reason, you need to remove an ontology you should use the command *remove_ontology*. Most data files you'll load depend on the ontologies (eg. fasta, gff, blast). You should **never** delete an ontology after having data files loaded.

.. code-block:: bash

    python manage.py remove_ontology --help

* This command requires the name of the ontology (Cv.name)
* There are dependencies between the Gene ontology records, therefore you need to delete the entry *external* first.
