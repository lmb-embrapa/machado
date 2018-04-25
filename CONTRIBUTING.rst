Contributing to machado
=======================

We welcome pull requests to fix bugs or add new features.

Licensing
---------

In your git commit and/or pull request, please explicitly state that you agree
to your contributions being licensed under the GNU General Public License version 3
as published by the Free Software Foundation (see our LICENSE.txt file for more
details).

Git Usage
---------

If you are planning to make a pull request, start by creating a new branch
with a short but descriptive name (rather than using your master branch).


Coding Conventions
------------------

machado tries to follow the coding conventions laid out in PEP8 and PEP257.

 - http://www.python.org/dev/peps/pep-0008/
 - http://www.python.org/dev/peps/pep-0257/

We use the tool ``flake8`` for code style checks, together with various
plugins which can be installed as follows::

    $ pip install flake8 flake8-docstrings flake8-rst-docstrings

You can then run ``flake8`` directly as follows::

    $ flake8 machado

Testing
-------

Any new feature or functionality will not be accepted without tests. Likewise
for any bug fix, we encourage including an additional test.

Local Testing
-------------

Please always run the style checks (see above) and the full test suite on
your local computer before submitting a pull request, e.g.::

	$ python manage.py test machado

Continous Integration
---------------------

Once you submit your pull request on GitHub, several automated tests should
be run, and their results reported on the pull request.

We use TravisCI to run the machado under Linux.

**The TravisCI checks must pass before your pull request will be merged.**
