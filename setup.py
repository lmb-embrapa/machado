"""Setup."""


import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="machado",
    version="v0.3.0",
    packages=find_packages(),
    include_package_data=True,
    license="GPL License",
    description="This library provides users with a framework to store, search and visualize biological data.",
    long_description=README,
    url="https://github.com/lmb-embrapa/machado",
    author="LMB",
    author_email="",
    classifiers=[
        "Environment :: Console",
        "Framework :: Django :: 2.2",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    scripts=["bin/fixChadoModel.py"],
    install_requires=[
        "django==2.2.13",
        "psycopg2-binary==2.8.5",
        "biopython==1.76",
        "obonet==0.2.5",
        "tqdm==4.45.0",
        "typing==3.7.4.1",
        "bibtexparser==1.1.0",
        "djangorestframework==3.11.0",
        "drf-yasg==1.17.1",
        "drf-nested-routers==0.91",
        "pysam==0.15.2",
    ],
    zip_safe=False,
)
