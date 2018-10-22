Visualization
=============

The *machado* API framework

JBrowse
-------

The `JBrowse <https://jbrowse.org>`_ software renders genomic tracks from Chado using the *machado* API.


**JBrowse**

Install JBrowse following the `official instructions <https://jbrowse.org/docs/installation.html>`_.

The *machado* source contains the directory extras. Copy the file extras/trackList.json.sample to the JBrowse data directory (eg. /var/www/html/jbrowse/data) and rename it to trackList.json

.. code-block:: bash

    cp extras/trackList.json.sample /var/www/html/jbrowse/data/trackList.json

Edit the file to set the **organism** name you have loaded to the database.


**machado API**

Start the *machado* API framework:

.. code-block:: bash

    python manage.py runserver
