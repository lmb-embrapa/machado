# Web Server

## Django manage runserver

Check if your server is working — test the machado server:

```bash
python manage.py runserver
```

Now, open your browser and go to <http://127.0.0.1:8000>.

Use `CTRL+C` to stop the web server.

## Django Apache WSGI

Before starting, make sure you have Apache installed in your system. In Ubuntu 20.04:

```bash
sudo apt install apache2
```

In order to have Apache2 hosting the Django applications, it's necessary to use WSGI. By doing this it won't be necessary to run the runserver command anymore — Apache will take care of this process. Install the following package:

```bash
sudo apt install libapache2-mod-wsgi-py3
```

Now configure Apache to use the WSGI module. Here is the configuration file (`/etc/apache2/sites-available/MYGENOME.conf`):

```apacheconf
<Directory "/var/www/MYGENOME/machadoproject">
    <Files "wsgi.py">
        Require all granted
    </Files>
</Directory>

Alias /MYGENOME/static/ /var/www/MYGENOME/staticfiles/

<Directory "/var/www/MYGENOME/staticfiles">
    Require all granted
</Directory>

WSGIDaemonProcess machadoproject python-home=/var/www/MYGENOME/.venv python-path=/var/www/MYGENOME lang='en_US.UTF-8' locale='en_US.UTF-8'
WSGIProcessGroup machadoproject
WSGIScriptAlias /MYGENOME /var/www/MYGENOME/machadoproject/wsgi.py
```

- In this example the whole project is in `/var/www/MYGENOME`, but it's not required to be there.
- This directory and sub-directories must have 755 permissions.
- Ensure the `python-home` path matches your virtual environment (`.venv`).

There must be a symlink of your config file in the sites-enabled directory:

```bash
sudo ln -s /etc/apache2/sites-available/MYGENOME.conf /etc/apache2/sites-enabled/MYGENOME.conf
```

In the `.env` file, ensure the following variables are set for production:

```bash
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
TIME_ZONE=America/Sao_Paulo

MACHADO_VALID_TYPES=gene,mRNA,polypeptide
```

Set `TIME_ZONE` to the server's actual timezone (defaults to `UTC` if unset). Django applies it at process startup, so it also determines what wall-clock time is recorded for timestamps such as the loader's command history — a mismatch here makes those timestamps look off relative to the server's local clock.

If you are running more than one machado instance on the same machine — for
example, several instances mounted at different Apache subpaths on the same
domain — set `URL_PREFIX` in each instance's `.env` to that instance's mount
path (e.g. `URL_PREFIX=/demo`). Without it, session/CSRF cookies and the
browser-stored accent color are not scoped per instance, so signing in or
picking a color in one instance can interfere with the others:

```bash
URL_PREFIX=/demo
```

Now, run `collectstatic` to gather the static files from all libraries to the `staticfiles` directory:

```bash
python manage.py collectstatic
```

It's necessary to restart the Apache2 service every time there are modifications on configuration files or source code updates:

```bash
sudo systemctl restart apache2.service
```

Now, open your browser and go to your configured domain (e.g., <http://yourdomain.com/MYGENOME>).
