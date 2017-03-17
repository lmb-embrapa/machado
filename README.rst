# Django Chado

Django Chado is a Django app that contains tools to interact with a Chado database.

Please make sure you have a Chado database up and running and your Django installation is configured to access it.
Detailed documentation can be found in the **docs** directory.


## Quick start

1. Download the package

        git clone https://azneto@bitbucket.org/azneto/django-chado.git


2. Install the package

        python setup.py install


3. Add "djangochado" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = [
            ...
            'chado',
        ]

