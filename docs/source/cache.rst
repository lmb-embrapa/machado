Cache (optional)
==================


The machado views are pre-configured to enable local-memory caching for 1 hour.
In order to move the cache to another location, you'll to set Django's cache framework following the `official instructions <https://docs.djangoproject.com/en/2.1/topics/cache/>`_.

**Example**

Include the following in the settings.py to store the cache in the database:

.. code-block:: bash

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'machado_cache_table',
        }
    }
    CACHE_TIMEOUT = 60 * 60 * 24  # 86400 seconds == 1 day


Create the cache table:

.. code-block:: bash

    python manage.py createcachetable

**Clearing the cache table**

It is a good idea to clear the cache table whenever you made changes to your machado installation.
For this intent, install the django-clear-cache tool `https://github.com/rdegges/django-clear-cache`

.. code-block:: bash

    pip install django-clear-cache

Then modify your settings.py file to add clear_cache:

.. code-block:: bash

    INSTALLED_APPS = (
    # ...
    'clear_cache',
    )

Then to clear the cache just run

.. code-block:: bash

    python manage.py clear_cache
