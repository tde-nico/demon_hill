import socket
import ssl
import time
import sys



SERVER_HOST = "fe80::215:5dff:fed9:2922"
if (len(sys.argv) > 1 and sys.argv[1] == '-l') \
	or (len(sys.argv) > 2 and sys.argv[2] == '-l'):
	SERVER_HOST = "::1"


SERVER_PORT = 1337
if (len(sys.argv) > 1 and sys.argv[1] == '-f') \
	or (len(sys.argv) > 2 and sys.argv[2] == '-f'):
	SERVER_PORT -= 1


IPV6 = 1
SSL = 0


if __name__ == "__main__":
	if IPV6:
		client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	else:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	if SSL:
		client = ssl.wrap_socket(client, ca_certs="./ca-cert.pem", do_handshake_on_connect=True)

	print(f'IPv6: {IPV6}, SSL: {SSL}')
	print(f'Connecting to {SERVER_HOST} {SERVER_PORT}')
	client.connect((SERVER_HOST, SERVER_PORT))

	i = 0
	while True:
		print(f'sending... {i}')
		client.sendall(f"Hello World! {i}".encode("utf-8"))
		print(client.recv(1024))
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
