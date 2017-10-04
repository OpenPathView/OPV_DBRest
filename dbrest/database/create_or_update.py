#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2017 Open Path View
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

# Contributors: BERNARD Benjamin
# Email: benjamin.bernard@openpathview.fr
# Description: Create or upgrade a database if it exists. This script use sqlalchemy-migrate

"""Database creation and migration script.

Usage:
  create_or_update.py (--db-uri=<path>) [--debug]
  create_or_update.py (-h | --help)

Options:
  -h --help                     Show this screen.
  --db-uri=<path>               Set the database location.
  --debug                       Set logger to debug level.
"""

import os
import sys
import logging
from docopt import docopt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists

from migrate.versioning import api as mapi
from migrate.versioning.util import load_model
from migrate.exceptions import DatabaseNotControlledError


logger = logging.getLogger("create_or_update")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logger.addHandler(ch)

def create_or_migrate(db_uri, db_repo, model_dotted_name):
    """
    Create or migrate a database.

    :param db_uri: Database URI.
    :param db_repo: Migrate repository.
    :param model_dotted_name: path to model in form of string: ``some.python.module:Class`
    """
    logger.info("Create or migrate database: {} with migrate repo: {}".format(db_uri, db_repo))

    # Test if the migrate repository exists
    if not os.path.isdir(db_repo):
        raise OSError(2, "Migrate repository doesn't exists ! ", db_repo)

    engine = create_engine(db_uri)
    dbExist = database_exists(db_uri)

    # Test if database exists, create it if needed
    if not dbExist:
        logger.info("Database {} doesn't exists.".format(db_uri))

        # Create db with meta model
        meta = load_model(model_dotted_name)
        meta.create_all(engine)

        # set version to latest number
        lastest_version_rep = mapi.version(db_repo)
        logger.debug("Lastest version in repo is {}, setting db to this version".format(lastest_version_rep))
        mapi.version_control(db_uri, db_repo, lastest_version_rep)

        # no updagrade needed we just created the lastest version available
        return

    # When db exist, checking if it's under version control
    try:
        v = mapi.db_version(db_uri, db_repo)
        logger.info("Database {} exists and is under version control (version: {})".format(db_uri, v))
    except DatabaseNotControlledError:  # DB isn't under version controlled
        mapi.version_control(db_uri, db_repo, 0)  # considering it's an old db, before versionning

    # upgrading to newest version
    logger.info("Upgrading database")
    mapi.upgrade(db_uri, db_repo)

def main():
    args = docopt(__doc__)

    if "--debug" in args and args['--debug']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # model import issue to current execution directory
    cur_dir = os.getcwd()
    sys.path.append(cur_dir)
    logger.debug("Added to sys path : {}".format(cur_dir))

    repo = os.path.dirname(os.path.realpath(__file__)) + "/migrate_repository"
    model_dotted_name = "dbrest.models:Base.metadata"

    create_or_migrate(db_uri=args['--db-uri'], db_repo=repo, model_dotted_name=model_dotted_name)

if __name__ == "__main__":
    main()
