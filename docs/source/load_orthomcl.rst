Loading OrthoMCL results
========================

Load OrthoMCL
-------------

.. code-block:: bash

    python manage.py load_orthomcl --filename groups.txt

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_orthomcl --help

=============   ==================================================================================
--filename 		groups.txt file *
--cpu 			Number of threads
=============   ==================================================================================

\* output result from OrthoMCL software. Mandatory.


Remove orthology
----------------

If, by any reason, you need to remove orthology relationships, you should use the command *remove_relationship --filename*. **Every orthologous relations from filename (e.g. 'groups.txt' from OrthoMCL) will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_relationship --help

* This command requires the file name 'groups.txt' used before as input to load orthologies.
