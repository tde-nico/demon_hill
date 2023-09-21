import socket
import ssl
import time
import sys

SERVER_HOST = "172.31.207.108"
if len(sys.argv) > 1:
	SERVER_HOST = "127.0.0.1"
SERVER_PORT = 1337

#ssl.SSLContext.maximum_version = ssl.TLSVersion.TLSv1_2

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client = ssl.wrap_socket(client, ca_certs="./ca-cert.pem", do_handshake_on_connect=True)

    client.connect((SERVER_HOST, SERVER_PORT))

    i = 0
    while True:
        print(f'sending... {i}')
        client.sendall(f"Hello World! {i}".encode("utf-8"))
        print(client.recv())
        i += 1
        time.sleep(1)
        

'''
hostname = 'www.python.org'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('./ca-cert.pem')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())
'''
