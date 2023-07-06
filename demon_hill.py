import importlib
import socket, select, threading
import os, sys, re
import logging
import random, string


##############################   MAIN   ##############################

if __name__ == '__main__':
	module = __file__.split('/')[-1].removesuffix('.py')
	this = importlib.import_module(module)

	if len(sys.argv) == 3:
		this.FROM_PORT = int(sys.argv[1])
		this.TO_PORT = int(sys.argv[2])

	proxy = this.TCPProxy(this.logger, '0.0.0.0', '127.0.0.1', this.FROM_PORT, this.TO_PORT)
	proxy.start()

	proxy.lock.acquire()
	if not proxy.sock:
		os._exit(0)
	proxy.lock.release()

	reload_string = this.to_rainbow('Reloading Proxy')

	while True:
		try:
			cmd = input()

			if cmd[:1] == 'q':
				proxy.close()
				proxy.lock.acquire()
				os._exit(0)

			elif cmd[:1] == 'r':
				this.logger.info(reload_string)
				importlib.reload(this)
				tmp_sock = proxy.sock
				proxy.is_running = False
				proxy.sample_connection()
				proxy.lock.acquire()
				proxy.lock.release()
				proxy = this.TCPProxy(this.logger, '0.0.0.0', '127.0.0.1', this.FROM_PORT, this.TO_PORT, tmp_sock)
				proxy.start()
			
			elif cmd[:1] == 'i':
				this.logger.info(this.to_rainbow(f'PID: {os.getpid()}'))
				this.logger.info(f'Threads: {threading.enumerate()}')

		except KeyboardInterrupt:
			proxy.close()
			proxy.lock.acquire()
			os._exit(0)
		except Exception as e:
			this.logger.error(str(e))




##############################   CONFIG   ##############################


LOG_LEVEL = 'info'

FROM_PORT = 1338
TO_PORT = 1337

SERVER_HISTORY_SIZE = 1024 * 1024
CLIENT_HISTORY_SIZE = 1024 * 1024


FLAG_LEN = 32
FLAG_REGEX = rb'[A-Z0-9]{31}='

REGEX_MASKS = [
	rb'1\n[a-zA-Z0-9]{3}\n\n5\n2\n[a-zA-Z0-9]*\n3\n0\n2\n',
]

REGEX_MASKS_2 = [
	#rb'filename=".*"',
]




##############################   UTILS   ##############################


def random_flag(length:int=FLAG_LEN-1):
	return "".join(random.choices(string.ascii_uppercase + string.digits, k=length)) + "="


def replace_flag(logger: logging.Logger, data: bytes, id: int) -> bytes:
	def callback(match_obj):
		new_flag = random_flag()
		logger.warning(f"{match_obj.group().decode()} -> {new_flag}")
		return new_flag.encode()

	logger.warning(f"Reciving Attack from {id}")
	search = re.search(FLAG_REGEX, data)
	if search:
		data = re.sub(FLAG_REGEX, callback, data)
	#else:
	#	data = b"HTTP/2 404 Not Found\n"
	return data


##############################   FILTERS   ##############################


def custom_filter(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:

	# write here

	return data


def regex_filter(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:
	for exclusion in REGEX_MASKS:
		if re.search(exclusion, client_history):
			data = replace_flag(logger, data, id)
			break
	return data


def regex_filter_2(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:
	for exclusion in REGEX_MASKS_2:
		res = re.search(exclusion, client_history)
		if res:
			filename = client_history[res.start():].split(b'"')[1]
			logger.critical(f"{filename}")
			if filename != b'program':
				data = replace_flag(logger, data, id)
				break
	return data


SERVER_FILTERS = [
	regex_filter,
]

CLIENT_FILTERS = [
]

##############################   LOGGER   ##############################

END				= "\033[0m"

BLACK			= "\033[30m"
RED				= "\033[31m"
GREEN			= "\033[32m"
YELLOW			= "\033[33m"
BLUE			= "\033[34m"
PURPLE			= "\033[35m"
CYAN			= "\033[36m"
GREY			= "\033[90m"

HIGH_RED		= "\033[91m"
HIGH_GREEN		= "\033[92m"
HIGH_YELLOW		= "\033[93m"
HIGH_BLUE		= "\033[94m"
HIGH_PURPLE		= "\033[95m"
HIGH_CYAN		= "\033[96m"

def to_rainbow(s: str) -> str:
	rainbow = [HIGH_PURPLE, HIGH_BLUE, HIGH_CYAN, HIGH_GREEN, HIGH_YELLOW, YELLOW, RED]
	colors = len(rainbow)
	i = 0
	res = ''
	for char in s:
		res += rainbow[i] + char
		i = (i + 1) % colors
	res += END
	return res

class CustomFormatter(logging.Formatter):
	fmt = "[%(asctime)s] %(levelname)s: %(message)s"
	FORMATS = {
		logging.DEBUG: GREY + fmt + END,
		logging.INFO: GREY + "[%(asctime)s] " + END + "%(levelname)s: %(message)s",
		logging.WARNING: YELLOW + "[%(asctime)s] %(levelname)s: " + HIGH_YELLOW + "%(message)s" + END,
		logging.ERROR: RED + fmt + END,
		logging.CRITICAL: HIGH_RED + fmt + END,
	}

	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno, self.fmt)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)



levels = {
	'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL,
}
log_level = levels.get(LOG_LEVEL.lower(), logging.INFO)


logger = logging.getLogger('demologger')
logger.handlers.clear()
custom_handler = logging.StreamHandler()
custom_handler.setLevel(log_level)
custom_handler.setFormatter(CustomFormatter())
logger.addHandler(custom_handler)
logger.setLevel(log_level)


##############################   MIDDLEWARE   ##############################


class Client2Server(threading.Thread):
	def __init__(self, logger:logging.Logger, to_host:str, to_port:int, client_sock:socket.socket, client_id:str):
		super(Client2Server, self).__init__()
		self.logger = logger
		self.client = client_sock
		self.id = client_id
		self.client_history = b""
		self.server_history = b""
		self.error = None
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.connect((to_host, to_port))
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
			data = read.recv(4096)
		except Exception as e:
			self.exit(f'{e}')

		if not data:
			self.exit("closed")

		# TODO better history
		if is_client:
			self.client_history += data
			filters = CLIENT_FILTERS
		else:
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
			logger.debug(f'{read_sockets} {write_sockets} {error_sockets}')

			if self.client.fileno() == -1 or self.server.fileno() == -1:
				self.exit(f'closed during select')

			for sock in read_sockets:
				if sock == self.client:
					self.send(self.client, self.server, True)
				elif sock == self.server:
					self.send(self.server, self.client, False)



##############################   PROXY   ##############################


class TCPProxy(threading.Thread):
	def __init__(self, logger:logging.Logger, from_host:str, to_host:str, from_port:int, to_port:int, sock:socket.socket=None):
		super(TCPProxy, self).__init__()
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
				self.logger.info(f"Serving {GREEN}{self.from_port}{END} -> {GREEN}{self.to_port}{END}")
			else:
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
			logger.debug(f'{read_sockets} {write_sockets} {error_sockets}')

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
						logger.error(f'{e}')
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


	def close(self):
		if self.sock:
			self.sock.close()
			self.sample_connection()


	def sample_connection(self):
		try:
			self.lock.acquire()
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.connect(('127.0.0.1', self.from_port))
			server.close()
		except ConnectionRefusedError as e:
			self.logger.warning(f'{e}')
		except Exception as e:
			self.logger.critical(f'{e}')

