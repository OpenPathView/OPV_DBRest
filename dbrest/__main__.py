#!/usr/bin/python3
# coding: utf-8
"""Api server and db

Usage:
  server.py run [options]
  server.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --db-location=<path>      Set the database location [default: postgres://postgres:postgres@localhost/opvtest].
  --rederbroID=<rederbroID> Set the rederbroID. [default: 1]
  --debug=False             Set debug mode [default: False]
  --port=<port>             The API http port [default: 5000]
"""

import os

from docopt import docopt

"""
 Make environnement config for API.
"""
def makeEnvironementConfig(arguments):
    exports = 'export OPVAPI_dbPath="' + arguments.get('--db-location') + '"'
    exports += ' && export OPVAPI_debug="' + arguments.get('--debug') + '"'
    exports += ' && export OPVAPI_rederbroID="' + arguments.get('--rederbroID') + '"'
    return exports

def main():
    arguments = docopt(__doc__)
    debug = bool(arguments.get('--debug'))
    os.system(makeEnvironementConfig(arguments) + ' && hug -m dbrest.api -p ' + arguments['--port'])

if __name__ == "__main__":
    main()
