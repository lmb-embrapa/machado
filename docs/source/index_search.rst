Index and search
================

**Haystack**

The `Haystack <https://haystacksearch.org>`_ software enables the Django framework to run third party search engines such as Elasticsearch and Solr. Even though you can use any search engine supported by Haystack, machado was tested using `Elasticsearch <https://www.elastic.co/products/elasticsearch>`_.

**Elasticsearch**

The latest Elasticsearch supported by Haystack is version 5.x.x
Install Elasticsearch following the `instructions <https://django-haystack.readthedocs.io/en/v2.4.1/installing_search_engines.html#elasticsearch>`_. "Elasticsearch requires Java 8 or later. Use the official Oracle distribution or an open-source distribution such as OpenJDK." So before continuing you should probably want to have java installed using the following command (ubuntu 20.04):

.. code-block:: bash

    sudo apt install openjdk-8-jdk

Now, proceding with elasticsearch instalation, run the following commands:

.. code-block:: bash

    cd YOURPROJECT
    source bin/activate
    cd src
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.3-amd64.deb
    sudo dpkg -i elasticsearch-7.17.3-amd64.deb
    sudo systemctl daemon-reload
    sudo systemctl enable elasticsearch.service
    sudo systemctl start elasticsearch.service

**Django Haystack**

Install django-haystack following the `official instructions <http://docs.haystacksearch.org/en/master/tutorial.html#installation>`_.


.. code-block:: bash

    pip install 'elasticsearch>=7,<8'

In the WEBPROJECT/settings.py file, add haystack to INSTALLED_APPS section.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'haystack',
        ...
    ]

The settings.py file should contain the `search engine configuration <http://docs.haystacksearch.org/en/master/tutorial.html#xapian>`_.

.. code-block:: bash

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'haystack',
        },
    }

* In the settings.py file, set the variable MACHADO_VALID_TYPES to restrict the types of features that will be indexed. Otherwise, every feature will be indexed.

.. code-block:: bash

    MACHADO_VALID_TYPES = ['gene', 'mRNA', 'polypeptide']


**Indexing the data**

Go to the WEBPROJECT directory and use the manage.py. Please notice that it's necessary to run rebuild_index if additional data is loaded to the database or if changes are made to the settings files.

.. code-block:: bash

    python manage.py rebuild_index

* Rebuilding the index can be faster if you increase the number of workers (-k).


The Elasticsearch server has a 10,000 results limit by default. In most cases it will not affect the results since they are paginated. The links to export .tsv or .fasta files might truncated the results because of this limit. You can increase it using the following command line:

.. code-block:: bash

   curl -XPUT "http://localhost:9200/haystack/_settings" -d '{ "index" : { "max_result_window" : 500000 } }' -H "Content-Type: application/json"
