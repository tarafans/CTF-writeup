#!/usr/bin/env python2

# ulimit -n 65535
# ref. https://gist.github.com/Integralist/3f004c3594bbf8431c15ed6db15809ae
import socket
import threading

bind_ip = '0.0.0.0'
bind_port = 8001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(40986)

print 'Listening on {}:{}'.format(bind_ip, bind_port)

def handle_client_connection(client_socket):
    request = client_socket.recv(1024)
    # print 'Received {}'.format(request)

    client_socket.send('AAAAAAAA\n')
    
    # wait
    client_socket.recv(1024)

while True:
    client_sock, address = server.accept()
    print 'Accepted connection from {}:{}'.format(address[0], address[1])
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,))
    client_handler.start()
