Web server
==========

Django manage runserver
-----------------------

Start the *machado* server:

.. code-block:: bash

    python manage.py runserver


Now, open your browser and go to http://127.0.0.1:8000

Use CTRL+C to stop the webserver.


Django Apache WSGI
------------------

In order to have Apache2 hosting the Django applications, it's necessary to use WSGI.

.. code-block:: bash

    apt install libapache2-mod-wsgi-py3


Here is the configuration file (/etc/apache2/sites-available/YOURPROJECT.conf)

.. code-block:: bash

    <Directory "/var/www/YOURPROJECT/WEBPROJECT/WEBPROJECT">
    <Files "wsgi.py">
        Require all granted
    </Files>

    Alias /static/ /var/www/YOURPROJECT/WEBPROJECT/static/

    <Directory "/var/www/YOURPROJECT/WEBPROJECT/static">
        Require all granted
    </Directory>

    </Directory>
    WSGIDaemonProcess WEBPROJECT
    WSGIPythonHome /var/www/YOURPROJECT
    WSGIPythonPath /var/www/YOURPROJECT/WEBPROJECT
    WSGIScriptAlias /YOURPROJECT /var/www/YOURPROJECT/WEBPROJECT/WEBPROJECT/wsgi.py

* In this example the whole project is in /var/www/YOURPROJECT, but it's not required to be there.
* This directory and sub-directories must have 755 permissions

There must be a symlink of your config file in the sites-enabled directory

.. code-block:: bash

    sudo ln -s /etc/apache2/sites-available/YOURPROJECT.conf /etc/apache2/sites-available/YOURPROJECT.conf


* In the WEBPROJECT/settings.py file, set the following variables:

.. code-block:: bash

    ALLOWED_HOSTS = ['*']
    STATIC_URL = '/static/'
    STATIC_ROOT = '/var/www/YOURPROJECT/WEBPROJECT/static'


Now, run collectstatic to gather the static files from all libraries to STATIC_ROOT.

.. code-block:: bash

    python manage.py collectstatic


It's necessary to restart the Apache2 service everytime there are modifications on configuration files or source code updates.

.. code-block:: bash

    sudo systemctl restart apache2.service


Now, open your browser and go to http://localhost/YOURPROJECT
