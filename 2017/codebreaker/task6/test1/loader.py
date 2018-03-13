from __future__ import print_function
import sys

class MetaImportFinder(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def find_module(self, fullname, path=None):
        if fullname == self.prefix:
            return get_importer()


def get_importer():
    if not hasattr(get_importer, 'zi'):
        import zipfile
        with zipfile.ZipFile(sys.executable, 'r') as z:
            zi = z.getinfo('__main__.py')
            data = zi.extra
        import base64
        data = base64.b64decode(data)

        def hide(b, k):
            return bytes([c ^ k[i % len(k)] ^ 165 for i, c in enumerate(b)])

        import os
        import datetime
        key = int(os.path.getmtime(sys.executable))
        import struct
        keyb = struct.pack('<L', key)
        data = hide(data, keyb)
        import zipimport
        import tempfile
        t = tempfile.NamedTemporaryFile()
        t.write(data)
        t.flush()
        t.seek(0)
        import os
        fpath = '/proc/%d/fd/%d' % (os.getpid(), t.fileno())
        if not zipfile.is_zipfile(fpath):
            print('File Corrupt')
            exit(100)
        zi = zipimport.zipimporter(fpath)
        get_importer.t = t
        get_importer.zi = zi
    return get_importer.zi

#sys.meta_path.append(MetaImportFinder('pyserver'))

def main():
    import pyserver.__main__
    pyserver.__main__.main()
