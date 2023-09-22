from .settings import *
from .filters import *
from .log import *


class Client2Server(threading.Thread):
	def __init__(self, logger:logging.Logger, to_host:str, to_port:int, client_sock:socket.socket, client_id:str):
		super().__init__()
		self.logger = logger
		self.client = client_sock
		self.id = client_id
		self.client_history = b""
		self.server_history = b""
		self.error = None
		try:
			if IPV6:
				self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			else:
				self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if SSL:
				self.server = ssl.wrap_socket(
					self.server,
					ca_certs=SSL_CA_CERT,
					do_handshake_on_connect=True,
				)
			self.server.connect((to_host, to_port))

			self.client.setblocking(False)
			self.server.setblocking(False)
		except ConnectionRefusedError as e:
			self.error = f'{e}'
			self.logger.warning(self.error)
		except Exception as e:
			self.error = f'{e}'
			self.logger.critical(self.error)


	def exit(self, msg):
		msg = f'{CYAN}{self.id}{END} ' + msg
		if self.client.fileno() != -1:
			self.client.close()
			msg = f'client ' + msg
			if self.server.fileno() != -1:
				msg = 'and ' + msg
		if self.server.fileno() != -1:
			self.server.close()
			msg = f'server ' + msg
		self.logger.info(f"{msg}")
		sys.exit()


	def send(self, read:socket.socket, write:socket.socket, is_client:bool):
		try:
			if SSL:
				data = read.recv()
			else:
				data = read.recv(1024)

		except ssl.SSLError as e:
			if e.errno == ssl.SSL_ERROR_WANT_READ:
				pass
			return
		except Exception as e:
			self.exit(f'{e}')

		if not data:
			self.exit("closed")

		# TODO better history
		if is_client:
			if len(self.client_history + data) <= CLIENT_HISTORY_SIZE:
				self.client_history += data
			filters = CLIENT_FILTERS
		else:
			if len(self.server_history + data) <= SERVER_HISTORY_SIZE:
				self.server_history += data
			filters = SERVER_FILTERS

		try:
			for f in filters:
				data = f(self.logger, data, self.server_history, self.client_history, self.id)
			write.sendall(data)

		except Exception as e:
			self.exit(f"{e}")


	def run(self):
		socket_list = [self.client, self.server]
		while True:
			read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
			self.logger.debug(f'{read_sockets} {write_sockets} {error_sockets}')

			if self.client.fileno() == -1 or self.server.fileno() == -1:
				self.exit(f'closed during select')

			for sock in read_sockets:
				if sock == self.client:
					self.send(self.client, self.server, True)
				elif sock == self.server:
					self.send(self.server, self.client, False)


# Log
logger.debug(__file__)
