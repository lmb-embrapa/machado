Loading publication files
=========================

Load publication
----------------

.. code-block:: bash

    python manage.py load_publication --file reference.bib

* Loading this file can be faster if you increase the number of threads (--cpu).

Remove publication
------------------

If, by any reason, you need to remove a publication you should use the command *remove_publication*. **If you delete a publication, every record that depend on it will be deleted on cascade, with the exception of the Dbxref field that contains the DOI accession**.

.. code-block:: bash

    python manage.py remove_publication --help

