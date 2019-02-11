Index and search
================

**Haystack**

The `Haystack <https://haystacksearch.org>`_ software enables the Django framework to run third party search engines such as Xapian, Whoosh, Solr and Elasticsearch. Such search engines will provide fast queries, boolean operators, wildcards, and facets. Even though you can use any search engine supported by Haystack, machado was tested using `Xapian <https://xapian.org>`_.

**Xapian**

Install xapian-haystack following the `instructions <https://github.com/notanumber/xapian-haystack>`_.


.. code-block:: bash

    cd YOURPROJECT
    source bin/activate
    cd src
    git clone https://github.com/notanumber/xapian-haystack.git
    cd xapian-haystack
    ./install_xapian.sh 1.4.9
    python setup.py install

**Django Haystack**

Install django-haystack following the `official instructions <http://docs.haystacksearch.org/en/master/tutorial.html#installation>`_.


.. code-block:: bash

    pip install django-haystack

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
            'ENGINE': 'xapian_backend.XapianEngine',
            'PATH': os.path.join(os.path.dirname(__file__), 'xapian_index'),
        },
    }

**Indexing the data**

.. code-block:: bash

    python manage.py rebuild_index
