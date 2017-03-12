#!/usr/bin/python3
# coding: utf-8
"""Api server and db

Usage:
  server.py run [options]
  server.py (-h | --help)

Options:
  -h --help             Show this screen.
  --db-location=<path>  Set the database location (e.g sqlite:////tmp/test.db) [default: in-memory].
  --host=<host>         The bind host [default: 0.0.0.0]
  --debug               Allow to stop the server on /shutdown
"""

from docopt import docopt

from . import server

def main():
    arguments = docopt(__doc__)
    debug = bool(arguments.get('--debug'))
    server.makeAndRun(arguments['--db-location'],
            arguments['--host'],
            debug=debug)

if __name__ == "__main__":
    main()
