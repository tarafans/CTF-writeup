# uncompyle6 version 2.14.1
# Python bytecode 3.5 (3350)
# Decompiled from: Python 3.5.2 (default, Nov 23 2017, 16:37:01) 
# [GCC 5.4.0 20160609]
# Embedded file name: app.py
# Compiled at: 1999-12-31 19:00:00
# Size of source mod 2**32: 6528 bytes
from .servercfg import logging_wrapper, ServerConfig, logging
from .compression import gzip_compress, deflate_to_gzip, gzip_decompress
import bottle
from bottle import route, request, response, HTTPError
from bottle import default_app as app_stack
from io import StringIO
__all__ = [
 'app']
bottle.BaseRequest.MEMFILE_MAX = 536870912

def new_app():
    return app_stack.push()


bottle_app = new_app()
bottle.TEMPLATE_PATH = []

@route('/new', method='post')
def queue_cmd():
    print('new: ' + request.POST['new'])
    uploaded = request.POST['new']
    cmd = uploaded.encode('latin1')
    config = request.environ['server.config']
    if config.cmd_auth is None:
        return 'xx\x00'
    elif config.clientid in config.cmd_auth:
        config.services.queue_push(cmd)
        return 'ok\x00'
    else:
        return 'no\x00'


@route('/next')
def next_cmd():
    config = request.environ['server.config']
    top = config.services.queue_top()
    if top is None:
        return ''
    else:
        uid, cmd = top
        return uid + b'\x00' + cmd


@route('/ack/<ack_id>')
def ack_cmd(ack_id):
    uid = decode_uid(ack_id)
    config = request.environ['server.config']
    if config.services.queue_drop(uid):
        return 'ok\x00'
    else:
        logging.error('item already acked: %r', uid)
        return 'no\x00'


def best_encoding(accept_encoding):
    options = [v.strip().split(';', 1) for v in accept_encoding.split(',')]
    best_option = None
    for opt in options:
        if len(opt) == 2:
            if not opt[1].startswith('q='):
                raise ValueError('bad Accept-Encoding header')
            try:
                weight = float(opt[1][2:])
            except:
                raise ValueError('bad Accept-Encoding header')

        else:
            weight = 1.0
        if best_option is None or best_option[1] < weight:
            best_option = (
             opt[0], weight)

    return best_option[0]


def decode_uid(uid):
    if len(uid) != 32:
        raise HTTPError(406)
    uid = uid.lower()
    if not all((c for c in '0123456789abcdef')):
        raise HTTPError(406)
    return uid.encode()


@route('/result/<uid>')
def result(uid):
    logging.debug('get result for %r' % (uid,))
    uid = decode_uid(uid)
    config = request.environ['server.config']
    result = config.services.get_result(uid)
    if result is None:
        logging.error('Response not found for: %r' % (uid,))
        raise HTTPError(404)
    else:
        encoding = best_encoding(request.headers.get('Accept-Encoding', 'gzip'))
        response.set_header('Content-Encoding', encoding)
        if encoding == 'gzip':
            return result
        if encoding == 'identity':
            return gzip_decompress(result)
        raise HTTPError(406)


@route('/upload/<uid>', method='post')
def upload(uid):
    print('upload for %r' % (uid,))
    logging.debug('upload for %r' % (uid,))
    uid = decode_uid(uid)
    uploaded = request.body.read()
    logging.debug('received size: %d' % (len(uploaded),))
    encoding = request.headers.get('Content-Encoding', 'identity')
    logging.debug('upload with encoding: %r' % (encoding,))
    if encoding == 'gzip':
        result = uploaded
    else:
        if encoding == 'identity':
            result = gzip_compress(uploaded)
        else:
            if encoding == 'deflate':
                result = deflate_to_gzip(uploaded)
            else:
                raise HTTPError(400)
            config = request.environ['server.config']
            config.services.put_result(uid, result)


def middleware(environ, start_response, exc_info=None):
    server_config = ServerConfig(environ, request)
    new_environ = environ.copy()
    new_environ['wsgi.errors'] = StringIO()
    new_environ['server.config'] = server_config
    squash_output = [
     False]
    started = [False]

    def my_start_response(status, headerlist, exc_info=None):
        logging.debug('my_start_response called with: %r, %r, None?%r' % (status, headerlist, exc_info == None))
        if exc_info is None:
            if not status.startswith('200 ') and not status.startswith('404 '):
                squash_output[0] = True
                bottle.abort(code=500, text='unknown error')
            else:
                started[0] = (status[:], headerlist[:])
        else:
            started[0] = (
             '500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html'), ('Content-Length', '0')])

    wrapped = logging_wrapper(bottle_app, server_config)
    result = wrapped(new_environ, my_start_response)
    if squash_output[0]:
        result = ''
    if not started[0]:
        start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html'), ('Content-Length', '0')])
    else:
        start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', '0')])
    return result


app = middleware
# okay decompiling app.pyc
