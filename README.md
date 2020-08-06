[![build-status-image]][travis]
[![cov-status-image]][codecov]
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4035/badge)](https://bestpractices.coreinfrastructure.org/projects/4035)

# machado

machado is a Django application that contains tools to interact with a Chado database.
It provides users with a framework to store, search and visualize biological data.
Detailed documentation can be found in the **docs** directory ([Read the docs](http://machado.readthedocs.io)).

## Features
- There are data loaders for the major bioinformatics formats: fasta, gff, obo, bibtex, blast, interproscan, orthomcl
- The machado API delivers data directly to the JBrowse genome browser
- The Haystack framework provides a very fast query interface using the Elasticsearch engine

## Installation
Please refer to the complete documentation at [Read the docs](http://machado.readthedocs.io/en/latest/installation.html).

## Docker

You can build your Machado instance using Docker: https://github.com/lmb-embrapa/machado-docker

## Demo

[https://www.machado.cnptia.embrapa.br](https://www.machado.cnptia.embrapa.br "machado demo")

## Contributing

machado is run by volunteers and we are always looking for people interested in helping with code development, documentation writing, and bug report.

If you wish to contribute, please create an issue.

## LICENSE

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
[cov-status-image]: https://img.shields.io/codecov/c/github/lmb-embrapa/machado/master.svg
[codecov]: https://codecov.io/gh/lmb-embrapa/machado

