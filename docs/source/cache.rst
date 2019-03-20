Cache (optional)
==================


The machado.urls are pre-configured to enable caching.
You just need to enable Django's cache framework following the `official instructions <https://docs.djangoproject.com/en/2.1/topics/cache/>`_.

**Example**

Include the following in the settings.py

.. code-block:: bash

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'machado_cache_table',
        }
    }
    CACHE_TIMEOUT = 60 * 60  # 3600 seconds == 1 hour


Create the cache table

.. code-block:: bash

    python manage.py createcachetable
