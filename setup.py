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
    # install_requires= ,
    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=False,
    url='https://github.com/OpenPathView/OPV_DBRest',
    entry_points={
        'console_scripts': [
            'opv-api=dbrest.__main__:main',
        ],
    }
)
