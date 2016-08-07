#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
import json
import random
import string
import os
from threading import Thread

from pogom import config
from pogom.app import Pogom
from pogom.models import create_tables, SearchConfig
from pogom.search import search_loop
from pogom.utils import get_args, get_encryption_lib_path

log = logging.getLogger(__name__)


def start_locator_thread():
    lib_path = get_encryption_lib_path()
    search_thread = Thread(target=search_loop, args=(lib_path,))

    search_thread.daemon = True
    search_thread.name = 'search_thread'
    search_thread.start()


def read_config():
    config_path = os.path.join(
        os.path.dirname(os.path.realpath(sys.argv[0])), "config.json")
    try:
        with open(config_path, "r") as f:
            c = json.loads(f.read())
    except:
        c = {}

    config['GOOGLEMAPS_KEY'] = c.get('GOOGLEMAPS_KEY', None)
    config['CONFIG_PASSWORD'] = c.get('CONFIG_PASSWORD', None)
    config['ACCOUNTS'] = c.get('ACCOUNTS', None)
    SearchConfig.update_scan_locations(c.get('SCAN_LOCATIONS', {}))

    if config.get('CONFIG_PASSWORD', None):
        config['AUTH_KEY'] = ''.join(random.choice(string.lowercase) for _ in range(32))


if __name__ == '__main__':
    args = get_args()

    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(asctime)s [%(module)11s] [%(levelname)7s] %(message)s')
    if not args.debug:
        logging.getLogger("peewee").setLevel(logging.INFO)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.WARNING)
        logging.getLogger("pogom.pgoapi.rpc_api").setLevel(logging.WARNING)
        logging.getLogger("pogom.models").setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.WARNING)
    elif args.debug == "info":
        logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.INFO)
        logging.getLogger("pogom.models").setLevel(logging.INFO)
        logging.getLogger("werkzeug").setLevel(logging.INFO)
    elif args.debug == "debug":
        logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("pogom.pgoapi.pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("pogom.models").setLevel(logging.DEBUG)
        logging.getLogger("werkzeug").setLevel(logging.INFO)

    create_tables()
    read_config()

    if (config.get('ACCOUNTS', None) and
            config.get('GOOGLEMAPS_KEY', None) and
            SearchConfig.SCAN_LOCATIONS):
        start_locator_thread()

    app = Pogom(__name__)
    config['ROOT_PATH'] = app.root_path
    app.run(threaded=True, debug=args.debug, host=args.host, port=args.port)
