[![build-status-image]][travis]
[![cov-status-image]][codecov]

# machado


machado is a Django app that contains tools to interact with a Chado database.
Detailed documentation can be found in the **docs** directory ([INSTALL](docs/INSTALL.md)).


## Quick start

1. Download the package

        git clone https://github.com/lmb-embrapa/machado.git


2. Install the package

        python setup.py install


3. Add "machado" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = [
            ...
            'machado',
            'rest_framework',
            ...
        ]

# LICENSE

machado - A Django implementation of Chado's schema.
Copyright (C) 2018 Embrapa

machado is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Additional permission under GNU GPL version 3 section 7

If you modify this Program, or any covered work, by linking or combining
it with Chado (or a modified version of that library), containing parts
covered by the terms of Artistic License 2.0, the licensors of this Program
grant you additional permission to convey the resulting work. {Corresponding
Source for a non-source form of such a combination shall include the source
code for the parts of Chado used as well as that of the covered work.}

See LICENSE.txt for complete gpl-3.0 license.

[build-status-image]: https://secure.travis-ci.org/lmb-embrapa/machado.svg?branch=master
[travis]: https://travis-ci.org/lmb-embrapa/machado
[cov-status-image]: https://img.shields.io/codecov/c/github/lmb-embrapa/machado.svg
[codecov]: https://codecov.io/gh/lmb-embrapa/machado
