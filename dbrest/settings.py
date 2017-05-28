"""
A module that contains all necessary settings.
Get settings from environment variable.
"""

import os

"""The path were to find the DB"""
engine_path = os.environ["OPVAPI_dbPath"]
debug = os.environ["OPVAPI_debug"] == "True" or os.environ["OPVAPI_debug"] == "true"
rederbroID = os.environ["OPVAPI_rederbroID"]
