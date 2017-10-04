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
# Description: Commit change in database model and version them for migration purposes.
#              This script use sqlalchemy-migrate
#              You need to run an old version of the database to generate the diff
#              and migrate to your new model.

"""Database model versionning script. Used to commit new models and migrate.

Usage:
  commit_db_model.py <commit-msg> (--db-uri=<path> --migrate-repo=<path> --model=<dottedmodel>) [--debug]
  commit_db_model.py (-h | --help)

Options:
  -h --help                     Show this screen.
  --db-uri=<path>               Set the database location.
  --migrate-repo=<path>         Migration (sqlalchemy-migrate) repository [default: db_repo].
  --model=<dottedmodel>         Path to sqlalchemy model in form of string: ``some.python.module:Class`.
  --debug                       Set logger to debug level.
"""

import os
import sys
import logging
from pathlib import Path
from docopt import docopt
from tempfile import TemporaryDirectory
from sqlalchemy_utils import database_exists

from migrate.versioning import api as mapi
from migrate.versioning.util import load_model

logger = logging.getLogger("commit_db_model")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logger.addHandler(ch)

def save_to_file(content, fpath):
    """
    Save a stringio stream in a file located at fpath.

    :param content: input string.
    :param fpath: output stream Path (posix).
    """
    with fpath.open(mode="w") as fd:
        fd.write(content)

def confirm(msg):
    """
    Confirm prompt.
    :param msg: Message to be display (question) in the console.

    :return: True if confirmed
    """
    confirm = input("{} [y/n] : ".format(msg))
    return confirm == '' or confirm == 'y' or confirm == 'yes'

def get_update_script_name(version, commit_msg):
    """
    Return update script name, based on the version of it and the commit message.

    :param version: version of the script.
    :param commit_msg: commit message.
    :return: 00x_commit_msg.py
    """
    m = commit_msg.replace(" ", "_")
    return "{0:03d}_{msg}_.py".format(int(version), msg=m)

def commit_db_model(db_uri, db_repo, model_dotted_name, commit_msg):
    logger.info("Committing new change on model : {}".format(model_dotted_name))

    # Test if the migrate repository exists
    if not os.path.isdir(db_repo):
        raise OSError(2, "Migrate repository doesn't exists ! ", db_repo)

    # Test if database exists, create it if needed
    if not database_exists(db_uri):
        raise IOError("Database {} doesn't exists, need to compare to the new model".format(db_uri))

    new_model = load_model(model_dotted_name)

    # Display detected changes to user
    print("------------------------------")
    print(mapi.compare_model_to_db(db_uri, db_repo, new_model))
    print("------------------------------")
    if not confirm("Are these changes correct ?"):
        logger.info("Changes not confirmed aborting :(")
        return

    with TemporaryDirectory(prefix="OPVDBMigrate") as temp_dir:
        sys.path.append(temp_dir)  # Used to read generated python
        old_model_fpath = Path(temp_dir) / "oldmodel.py"

        # generating old model from database
        logger.info("Generated old model python script from database")
        old_model_source = mapi.create_model(db_uri, db_repo)
        logger.debug("Old model python : \n {}".format(old_model_source))
        save_to_file(old_model_source, old_model_fpath)

        # get latest version
        new_version = mapi.version(db_repo) + 1
        update_script_path = Path(db_repo) / "versions" / get_update_script_name(new_version, commit_msg)
        logger.debug("Lastest version in repository {} is {}".format(db_repo, new_version))

        # make_update_script_for_model, save it in repo lastest_version + 1 + commit msg
        oldmodel = load_model('oldmodel:meta')
        update_script_source = mapi.make_update_script_for_model(db_uri, db_repo, oldmodel, new_model)
        save_to_file(update_script_source, update_script_path)

        if confirm("Did you check (and modify if necessary) the upgrade script ({}) ? !! Confirm will upgrade the database !!".format(update_script_path)):
            logger.info("Upgrading the database")
            # upgrade
            mapi.upgrade(db_uri, db_repo)
            logger.info("Migration done and versionned :) ")
        else:
            logger.info("Removing the update script")
            os.unlink(update_script_path)

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

    logger.debug(args)
    commit_db_model(db_uri=args['--db-uri'], db_repo=args['--migrate-repo'], model_dotted_name=args['--model'], commit_msg=args['<commit-msg>'])


if __name__ == "__main__":
    main()
