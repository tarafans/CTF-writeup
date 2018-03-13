# uncompyle6 version 2.12.0
# Python bytecode 3.5 (3350)
# Decompiled from: Python 2.7.12 (default, Nov 20 2017, 18:23:56) 
# [GCC 5.4.0 20160609]
# Embedded file name: main.py
# Compiled at: 1999-12-31 16:00:00
# Size of source mod 2**32: 1172 bytes
from . import secwsgi3
from .app import app
from .services import get_services
import sys
import io

def main():
    sys.stdout = io.TextIOWrapper(io.open(sys.stdout.fileno(), 'wb', 0), encoding=sys.stdout.encoding, write_through=True)
    sys.stderr = io.TextIOWrapper(io.open(sys.stderr.fileno(), 'wb', 0), encoding=sys.stderr.encoding, write_through=True)
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    HOST = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
    services = get_services()
    server = secwsgi3.get_server(HOST, PORT, app, services.child_setup)
    services.init()
    try:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Exitting')

    finally:
        services.fini()