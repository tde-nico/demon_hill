import socket
import ssl


HOST = "::1"
PORT = 1337

IPV6 = 1
SSL = 0



if __name__ == "__main__":
	if IPV6:
		server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	else:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	if SSL:
		server = ssl.wrap_socket(
			server,
			server_side=True,
			keyfile="server-key.pem",
			certfile="./server-cert.pem",
			do_handshake_on_connect=True,
		)

	server.bind((HOST, PORT))
	print(f'IPv6: {IPV6}, SSL: {SSL}')
	print(f'Listening on {HOST} {PORT}')
	server.listen(0)


	while True:
		#ssl.SSLContext.num_tickets = 0
		connection, client_address = server.accept()

		while True:
			#ssl.SSLContext.num_tickets = 0
			data = connection.recv(1024)

			if not data:
				break

			print(f"Received: {data.decode('utf-8')}")
			connection.sendall(b'ok')
