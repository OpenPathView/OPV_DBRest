#!/usr/bin/python3
# coding: utf-8

# Copyright (C) 2017 Open Path View, Maison Du Libre
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

# Contributors: Benjamin BERNARD <benjamin.bernard@openpathview.fr>
# Email: team@openpathview.fr
# Description: Export endpoint.

""" OPV partial export tool.
Usage:
    opv-export [options] <db-uri> <table-list>

Arguments:
    db-uri                   URI of the postgres database, for instance : postgresql://pg_dump_test:pg_dump_test@localhost:5432/pg_dump_test
    table-list               List of the table that needs to be exported, separated by commas (related tables will automatically be exported).
                             Eg : 'table1,table2,table3'

Options:
    -h --help                   Show this screen.
    --filters=<SQL>             SQL filters. Eg: mytable.mycol = 'value' AND myothertable.toto LIKE 'titi'
    --output-sql=<str>          Data will be dumped there. [default: dump.sql]
    --output-dm-list-file=<str> Directory manager list, if dm ids needs to be exported. [Default: dm_uuids.txt]
    --dm-cols=<str>             Wanted Directory manager uuids columns list. Eg : "panorama.equirectangular_path,lot.pictures_path"
    --debug                     Set logs to debug.
"""

import logging
from docopt import docopt
from dbrest.export import ExportDatasService
from pg_dump_filtered import model

def main():
    # --- Logs // Console only
    formatter_c = logging.Formatter('%(name)-30s: %(levelname)-8s %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter_c)
    rootLogger = logging.getLogger()
    rootLogger.addHandler(ch)
    logger = logging.getLogger(__name__.split(".")[0])

    # parsing aguments
    args = docopt(__doc__)
    db_uri = args["<db-uri>"]
    tables_to_export = args["<table-list>"].split(",")
    filters = args["--filters"]
    output_dump_sql = args["--output-sql"]
    dm_cols = [model.ColumnRef(table_name=c_str.split(".")[0], column_name=c_str.split(".")[1]) for c_str in args["--dm-cols"].split(",")]
    output_list_dm_file = args["--output-dm-list-file"]

    # setting logger level
    logger.setLevel(logging.DEBUG if "--debug" in args and args["--debug"] else logging.INFO)

    # printing parameters
    logger.info("Dumping datas :")
    logger.info(" DB : %s", db_uri)
    logger.info(" Table that will be exported : %r", tables_to_export)
    logger.info(" Filters applied : %s", filters)
    logger.info(" DM columns that will be listed : %r", dm_cols)
    logger.info(" -> Ouput file : %s", output_dump_sql)
    logger.info(" -> Output DM list file : %s", output_list_dm_file)

    export_service = ExportDatasService(db_uri=db_uri)
    export_service.dump_data(tables_to_export=tables_to_export, sql_filters=filters, output_file=output_dump_sql)
    export_service.generate_dm_list(tables_to_export=tables_to_export, dm_columns=dm_cols, sql_filters=filters, output_list_file=output_list_dm_file)

if __name__ == "__main__":
    main()
