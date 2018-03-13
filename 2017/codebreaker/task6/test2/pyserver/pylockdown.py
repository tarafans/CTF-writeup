# uncompyle6 version 2.12.0
# Python bytecode 3.5 (3350)
# Decompiled from: Python 2.7.12 (default, Nov 20 2017, 18:23:56) 
# [GCC 5.4.0 20160609]
# Embedded file name: pylockdown.py
# Compiled at: 1999-12-31 16:00:00
# Size of source mod 2**32: 7382 bytes
from __future__ import print_function
import sys
import os
import traceback
libc = None

def setup():
    global cached_gmtime
    global libc
    global locked_time
    sys.meta_path.append(MetaImportFinder('readline'))
    from ctypes import CDLL
    c = CDLL('')
    c_syscall = c.syscall
    sys.locked = False
    sys.sec = c
    libc = c

    def myexit(x):
        is_64 = sys.maxsize > 4294967296
        exit_num = 60 if is_64 else 1
        c_syscall(exit_num, x)

    sys.exit = myexit
    os._exit = myexit
    if orig_fileobject != object:
        socket.__dict__['_fileobject'] = safe_fileobject
    socket.__dict__['getfqdn'] = lambda s: 'unknown'
    import time
    locked_time = time.time()
    time.time = safe_time
    cached_gmtime = time.gmtime()
    time.gmtime = my_gmtime
    time.localtime = my_gmtime


cached_gmtime = None

def my_gmtime(*args, **kwargs):
    return cached_gmtime


locked_time = None

def safe_time():
    global locked_time
    locked_time += 1
    return locked_time


def lockdown():
    sys.path[:] = []
    sys.sec.prctl(22, 1, 0, 0, 0)
    sys.locked = True


import socket
try:
    orig_fileobject = socket._fileobject
except:
    orig_fileobject = object

if hasattr(socket, 'SocketIO'):
    import io

    class Safe_SocketIO(socket.SocketIO):

        def __init__(self, sock, mode):
            if mode not in ('r', 'w', 'rw', 'rb', 'wb', 'rwb'):
                raise ValueError('invalid mode: %r' % mode)
            io.RawIOBase.__init__(self)
            self._sock = safe_sock(sock)
            if 'b' not in mode:
                mode += 'b'
            self._mode = mode
            self._reading = 'r' in mode
            self._writing = 'w' in mode
            self._timeout_occurred = False


    socket.SocketIO = Safe_SocketIO

class safe_fileobject(orig_fileobject):

    def __init__(self, _sock, *args, **kwargs):
        orig_fileobject.__init__(self, safe_sock(_sock), *args, **kwargs)


try:
    from SocketServer import _eintr_retry
except ImportError:

    def _eintr_retry(f, *args, **kwargs):
        return f(*args, **kwargs)


def write(fd, d):
    if isinstance(d, str):
        return os.write(fd, d.encode())
    return os.write(fd, d)


def safe_send(self, b):
    fd = self.fileno()
    return write(fd, b)


def safe_sendall(self, b):
    fd = self.fileno()
    return safe_writeall(fd, b)


def safe_writeall(fd, b):
    total_written = 0
    blen = len(b)
    while total_written != blen:
        towrite = blen - total_written
        written = _eintr_retry(write, fd, b[total_written:])
        if written == towrite:
            break

    return total_written


import errno

def safe_writeall_async(fd, b, on_not_ready):
    total_written = 0
    blen = len(b)
    while total_written != blen:
        towrite = blen - total_written
        try:
            written = _eintr_retry(write, fd, b[total_written:])
        except OSError as e:
            if e.errno != errno.EAGAIN:
                raise
            giveup = on_not_ready(total_written)
            if giveup:
                break
            written = 0

        if written == towrite:
            break

    return total_written


def safe_recv(self, sz, flags=0):
    fd = self.fileno()
    return _eintr_retry(os.read, fd, sz)


def safe_recv_into(self, b, nbytes=0, flags=0):
    sz = len(b) if nbytes == 0 else nbytes
    data = safe_recv(self, sz, flags)
    len_data = len(data)
    view = memoryview(b)
    view[:len_data] = data
    del view
    del data
    return len_data


try:
    import wrapt
    enable_safesock = True
except ImportError:
    enable_safesock = False

if enable_safesock:

    class wrapt_SockProxy(wrapt.ObjectProxy):

        def sendall(self, *args, **kwargs):
            return safe_sendall(self, *args, **kwargs)

        def recv(self, *args, **kwargs):
            return safe_recv(self, *args, **kwargs)

        def send(self, *args, **kwargs):
            return safe_send(self, *args, **kwargs)

        def recv_into(self, *args, **kwargs):
            return safe_recv_into(self, *args, **kwargs)


    def safe_sock(_sock):
        return wrapt_SockProxy(_sock)


    fs = traceback.FrameSummary

    class wrapt_FrameSummary(fs):

        def __init__(self, *args, **kwargs):
            if getattr(sys, 'locked', False):
                kwargs['lookup_line'] = True
                kwargs['line'] = '...'
            return fs.__init__(self, *args, **kwargs)


    traceback.FrameSummary = wrapt_FrameSummary
else:

    def safe_sock(_sock):
        return _sock


import sys
import imp

class MetaImportFinder(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def find_module(self, fullname, path=None):
        name_parts = fullname.split('.')
        if name_parts and name_parts[0] == self.prefix:
            return MetaImportLoader(path)


class MetaImportLoader(object):

    def __init__(self, path_entry):
        self.path_entry = path_entry

    def load_module(self, fullname):
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
            mod.get_completer = lambda : None
            mod.set_completer = lambda *x: None
            mod.parse_and_bind = lambda *x: None
        mod.__file__ = fullname
        mod.__name__ = fullname
        mod.__path__ = [
         'path-entry-goes-here']
        mod.__loader__ = self
        mod.__package__ = '.'.join(fullname.split('.')[:-1])
        return mod


if not hasattr(sys, 'sec'):
    setup()
