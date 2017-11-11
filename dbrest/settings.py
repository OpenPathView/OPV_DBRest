"""
A module that contains all necessary settings.
Get settings from environment variable.
"""

import os

"""The path were to find the DB"""
OPVAPI_dbPath = os.environ["OPVAPI_dbPath"] if "OPVAPI_dbPath" in os.environ else None
OPVAPI_debug = os.environ["OPVAPI_debug"] if "OPVAPI_debug" in os.environ else None
OPVAPI_IDMalette = os.environ["OPVAPI_IDMalette"] if "OPVAPI_IDMalette" in os.environ else None

engine_path = OPVAPI_dbPath
debug = OPVAPI_debug == "True" or OPVAPI_debug == "true"
IDMalette = OPVAPI_IDMalette
