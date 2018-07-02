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
# Description: Entry point to export data DB dump + DM list.

import logging
import psycopg2
import tempfile
from typing import List
from urllib.parse import urlparse

from pg_dump_filtered import PgDumpFiltered
from pg_dump_filtered.model import ColumnRef

REQ_DM_ROW = """
SELECT {c.table_name}.{c.column_name} FROM {from_table}
{join_req}
{where}
"""

REQ_SELECT_DUMP = "COPY ({select}) TO STDOUT"

class ExportDatasService():

    def __init__(self, db_uri: str):
        """
        Initalize ExportDatasService.

        :param db_uri: Database URI.
        """
        self.logger = logging.getLogger(__name__)

        db_uri_parsed = urlparse(db_uri)
        self._db_conn = psycopg2.connect(
            database=db_uri_parsed.path[1:],
            user=db_uri_parsed.username,
            password=db_uri_parsed.password,
            host=db_uri_parsed.hostname)

        self._dump_service = PgDumpFiltered(
            db_conn=self._db_conn,
            ignored_constraints=["lot_id_tile_fkey"])

    def dump_data(self, tables_to_export: List[str], sql_filters: str=None, output_file: str="datas.sql"):
        """
        Dump partial data.

        :param table_to_export: List of table names that needs to be exported.
        :param sql_filters: SQL filter (WHERE statement), that will filtered the dump. Eg: tablename.col = value AND ...
        :param output_file: Path of the dump file.
        """
        self.logger.debug("Dumping data with filter : %s, to file : %s", sql_filters, output_file)

        self._dump_service.sql_filters = sql_filters
        self._dump_service.dump_file_path = output_file
        self._dump_service.dump(tables_to_export=tables_to_export)

    def generate_dm_list(self, tables_to_export: List[str], dm_columns=List[ColumnRef], sql_filters: str=None, output_list_file: str="datas_dm.txt"):
        """
        Generate directory manager archive.

        :param sql_filters: SQL filter (WHERE statement), that will filtered the dump. Eg: tablename.col = value AND ...
        :param dm_columns: List of DM columns that uses want to be exported.
                           Will execute a request for each columns and dump it's value to a tempory file use to list directories UUID for archiving CLI.
        :param output_archive: Path of the archive file.
        """
        self.logger.debug("Generating Directory Manager archive, with filter : %s, will be saved to : %s", sql_filters, output_list_file)
        _, join_req = self._dump_service.generate_tables_to_request_and_join(tables_to_export=tables_to_export)

        where = "" if sql_filters == "" or sql_filters is None else " WHERE " + sql_filters

        with open(output_list_file, "w") as uuids_list_file:

            for dm_col in dm_columns:
                select_request = REQ_DM_ROW.format(c=dm_col, from_table=tables_to_export[0], join_req=join_req, where=where)

                # Generate dump directly to a tempory file
                cur = self._db_conn.cursor()
                cur.copy_expert(REQ_SELECT_DUMP.format(select=select_request), uuids_list_file)
