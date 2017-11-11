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
# Description:  Create a database, based on original_model.py, used for test migration purposes.

"""Create a database, based on original_model.py, used for test migration purposes.

Usage:
  create_db_original.py <malette-id> (--db-uri=<path>) [--debug]
  create_db_original.py (-h | --help)

Options:
  -h --help                     Show this screen.
  --db-uri=<path>               Set the database location.
  --malette-id                  Malette id.
  --debug                       Set logger to debug level.
"""

import sys
import logging
import original_model
from docopt import docopt
from sqlalchemy import create_engine

logger = logging.getLogger("create_db_original")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

malette_id = 0

def get_malette_id():
    return malette_id

def createDb(db_uri):
    """
    Create original db, with postgis activated.

    :param db_uri: Database uri.
    """
    logger.info("Creating database ...")
    engine = create_engine(db_uri)

    original_model.Base.metadata.create_all(engine)

if __name__ == "__main__":
    args = docopt(__doc__)

    if "--debug" in args and args['--debug']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    malette_id = int(args["<malette-id>"])
    logger.info("Malette id is : {}".format(malette_id))
    createDb(args["--db-uri"])
