# uncompyle6 version 2.12.0
# Python bytecode 3.5 (3350)
# Decompiled from: Python 2.7.12 (default, Nov 20 2017, 18:23:56) 
# [GCC 5.4.0 20160609]
# Embedded file name: secwsgi3.py
# Compiled at: 1999-12-31 16:00:00
# Size of source mod 2**32: 3385 bytes
from .pylockdown import lockdown
import socketserver
import signal
import wsgiref
import errno
import sys
import os
import logging.config
import http
from http import client as _client
http.__dict__['client'] = _client
import http.server
import urllib
from urllib import parse as _parse
urllib.__dict__['parse'] = _parse
import wsgiref.simple_server
from wsgiref.handlers import CGIHandler
from wsgiref.simple_server import demo_app, make_server

class Safe_ForkingMixIn(socketserver.ForkingMixIn):

    def collect_children(self):
        if signal.getsignal(signal.SIGCHLD) in (signal.SIG_IGN, signal.SIG_DFL):
            return super(Safe_ForkingMixIn, self).collect_children()
        self.active_children = None

    def process_request(self, request, client_address):
        """Fork a new subprocess to process the request."""
        self.collect_children()
        pid = os.fork()
        if pid:
            if self.active_children is None:
                self.active_children = set()
            self.active_children.add(pid)
            self.close_request(request)
            return
        try:
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
            self.socket.close()
            os.environ.clear()
            wsgiref.handlers.BaseHandler.os_environ = dict()
            self.child_setup()
            lockdown()
        except:
            os._exit(1)

        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
            os._exit(0)
        except:
            try:
                self.handle_error(request, client_address)
                self.shutdown_request(request)
                os._exit(1)
            finally:
                os._exit(1)

    def shutdown_request(self, request):
        pass


def get_server(HOST, PORT, app, setup):

    class Safe_ForkingWSGIServer(Safe_ForkingMixIn, wsgiref.simple_server.WSGIServer):

        def child_setup(self):
            setup(self)

    return make_server(HOST, PORT, app, server_class=Safe_ForkingWSGIServer)