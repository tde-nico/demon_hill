from .settings import *
from .log import *
from .client2server import *
from .tables import *

from os import _exit
from importlib import import_module, reload

PACKAGE = 'demon_hill'

def load_module(name):
	mdl = import_module(name, package=PACKAGE)
	reload(mdl)
	if "__all__" in mdl.__dict__:
		names = mdl.__dict__["__all__"]
	else:
		names = [x for x in mdl.__dict__ if not x.startswith("_")]
	globals().update({k: getattr(mdl, k) for k in names})

load_module('.client2server')


class TCPProxy(threading.Thread):
	def __init__(self, logger:logging.Logger, from_host:str, to_host:str, from_port:int, to_port:int, sock:socket.socket=None):
		super().__init__()
		self.logger = logger
		self.from_host = from_host
		self.to_host = to_host
		self.from_port = from_port
		self.to_port = to_port
		self.sock = sock
		self.is_running = True
		self.lock = threading.Lock()
		self.lock.acquire()


	def run(self):
		try:
			if not self.sock:
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.sock.bind((self.from_host, self.from_port))
				self.sock.listen(1)
				self.logger.info(f"Serving {BLUE}{self.from_host}{END}:{GREEN}{self.from_port}{END}" +\
								f" -> {BLUE}{self.to_host}{END}:{GREEN}{self.to_port}{END}")
			else:
				self.logger.info(f"{BLUE}{self.from_host}{END}:{GREEN}{self.from_port}{END}" +\
								f" -> {BLUE}{self.to_host}{END}:{GREEN}{self.to_port}{END}")
				self.logger.info(f"{to_rainbow('Proxy Successfully Reloaded')}")
			self.lock.release()

		except Exception as e:
			self.logger.critical('Error while opening Main Socket')
			self.logger.critical(f'{e}')
			self.sock.close()
			self.sock = None
			self.lock.release()
			return


		while True:

			socket_list = [self.sock]
			read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
			self.logger.debug(f'{read_sockets} {write_sockets} {error_sockets}')

			if not self.is_running:
				break

			if self.sock.fileno() == -1:
				self.logger.info(f"Shutting {HIGH_RED}{self.from_port}{END} -> {HIGH_RED}{self.to_port}{END}")
				break

			if not read_sockets:
				continue

			for sock in read_sockets:
				if sock == self.sock:
					try:
						client_sock, addr = sock.accept()
						client_ip, client_port = addr
						client_id = f"{client_ip}:{client_port}"
						self.logger.info(f"client {CYAN}{client_id}{END} connected")
					except OSError as e:
						self.logger.error(f'{e}')
					break
			else:
				continue

			middleware = Client2Server(
				self.logger,
				self.to_host,
				self.to_port,
				client_sock,
				client_id
			)
			if not middleware.error:
				middleware.start()
		
		self.logger.info(f"{to_rainbow('Proxy Closed')}")
		self.lock.release()


	def sample_connection(self):
		try:
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.connect((LOCALHOST, self.from_port))
			server.close()
		except ConnectionRefusedError as e:
			self.logger.warning(f'{e}')
		except Exception as e:
			self.logger.critical(f'{e}')


	def close(self):
		if self.sock:
			self.sock.close()
			self.sample_connection()
	

	def exit(self):
		if AUTO_SET_TABLES:
			disable_forwarding(self.logger)
		self.lock.acquire()
		self.close()
		self.lock.acquire()
		_exit(0)


# Log
logger.debug(__file__)
