Web server
==========

Django manage runserver
-----------------------

Check if your server is working, test the *machado* server:

.. code-block:: bash

    python manage.py runserver


Now, open your browser and go to http://127.0.0.1:8000

Use CTRL+C to stop the webserver.


Django Apache WSGI
------------------
Before starting, make sure you have Apache installed in your system. In Ubuntu 18.04,
do:

.. code-block:: bash

    sudo apt install apache2

In order to have Apache2 hosting the Django applications, it's necessary to use WSGI.
By doing this it won't be necessary to run the runserver command anymore, Apache will
take care of this process. It will be necessary to install the following package:

.. code-block:: bash

    sudo apt install libapache2-mod-wsgi-py3

Now symlink the directory of YOURPROJECT to '/var/www/' (tested in Ubuntu 18.04):

.. code-block:: bash

    sudo ln -s /FULL/PATH/TO/YOURPROJECT /var/www/

* Make sure this directory and sub-directories have 755 permissions

Now configure Apache to use the WSGI module.
Here is the configuration file (/etc/apache2/sites-available/YOURPROJECT.conf)

.. code-block:: bash

    <Directory "/var/www/YOURPROJECT/WEBPROJECT/WEBPROJECT">
    <Files "wsgi.py">
        Require all granted
    </Files>
    </Directory>

    Alias /YOURPROJECT/static/ /var/www/YOURPROJECT/WEBPROJECT/static/

    <Directory "/var/www/YOURPROJECT/WEBPROJECT/static">
        Require all granted
    </Directory>

    WSGIDaemonProcess WEBPROJECT
    WSGIPythonHome /var/www/YOURPROJECT
    WSGIPythonPath /var/www/YOURPROJECT/WEBPROJECT
    WSGIScriptAlias /YOURPROJECT /var/www/YOURPROJECT/WEBPROJECT/WEBPROJECT/wsgi.py

* In this example the whole project is in /var/www/YOURPROJECT, but it's not required to be there.
* This directory and sub-directories must have 755 permissions

There must be a symlink of your config file in the sites-enabled directory

.. code-block:: bash

    sudo ln -s /etc/apache2/sites-available/YOURPROJECT.conf /etc/apache2/sites-enabled/YOURPROJECT.conf


* In the WEBPROJECT/settings.py file, set the following variables:

.. code-block:: bash

    ALLOWED_HOSTS = ['*']
    MACHADO_URL = 'http://localhost/YOURPROJECT'
    STATIC_URL = '/YOURPROJECT/static/'
    STATIC_ROOT = '/var/www/YOURPROJECT/WEBPROJECT/static'


Now, run collectstatic to gather the static files from all libraries to STATIC_ROOT.

.. code-block:: bash

    python manage.py collectstatic


It's necessary to restart the Apache2 service everytime there are modifications on configuration files or source code updates.

.. code-block:: bash

    sudo systemctl restart apache2.service


Now, open your browser and go to http://localhost/YOURPROJECT
