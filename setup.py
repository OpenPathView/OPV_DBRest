#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='dbrest',
    packages=find_packages(),
    author="",
    author_email="",
    description="The OPV DB rest api ",
    long_description=open('README.md').read(),
    dependency_links=["git+https://github.com/OpenPathView/OPV_DBRest-client.git#egg=opv_api_client-0.2"],
    install_requires=[
        "GeoAlchemy2",
        "hug",
        "marshmallow-sqlalchemy",
        "SQLAlchemy",
        "psycopg2",
        "gunicorn",
        "sqlalchemy-migrate",
        "docopt"
    ],
    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=True,
    url='https://github.com/OpenPathView/OPV_DBRest',
    entry_points={
        'console_scripts': [
            'opv-api=dbrest.__main__:main',
            'opv-db-migrate=dbrest.database.create_or_update:main'
        ],
    }
)
