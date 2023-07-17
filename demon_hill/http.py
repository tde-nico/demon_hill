from collections import UserDict
from re import compile
from .log import *
from .utils import *


HEADER = compile(r'([^:]+):\s+(.+)')
REQUEST = compile(r"(\w+)\s+(.+)\s+HTTP\/(\d\.\d|\d)")
RESPONSE = compile(r"HTTP\/(\d\.\d|\d)\s+(\d+)\s+(.+)")



class MalformedHeaderException(Exception):
	def __init__(self, message):
		custom_msg = f'MalformedHeaderException: {message}'
		super().__init__(custom_msg)


class MalformedRequestLineException(Exception):
	def __init__(self, message):
		custom_msg = f'MalformedRequestLineException: {message}'
		super().__init__(custom_msg)


class MalformedResponseLineException(Exception):
	def __init__(self, message):
		custom_msg = f'MalformedResponseLineException: {message}'
		super().__init__(custom_msg)


class HTTPHeaders(UserDict):
	def __init__(self, data: bytes) -> None:
		self.data: dict = {}
		for line in data.split(b'\n'):
			line = line.strip().decode()
			if not line:
				break
			match = HEADER.match(line)
			if not match:
				raise MalformedHeaderException(line)
			key: str = match.group(1)
			value: str = match.group(2)
			self[key] = value

	def __getitem__(self, item: str) -> str:
		return self.data[item.lower()]

	def __setitem__(self, item: str, value: str) -> None:
		self.data[item.lower()] = value



class HTTPPayload:
	def __init__(self, data: bytes) -> None:
		self.headers: HTTPHeaders = HTTPHeaders(data)
		self.body: bytes = b''
		if "content-length" in self.headers:
			self.body = data.split(b'\r\n\r\n', 1)[1]

	def __bytes__(self) -> bytes:
		result = bytearray()
		for key, value in self.headers.items():
			result.extend(f"{key}: {value}\r\n".encode())
		result.extend(b"\r\n")
		if self.body:
			result.extend(self.body)
		return bytes(result)


class HTTPRequest:
	def __init__(self, data: bytes) -> None:
		if b'\n' not in data:
			raise MalformedRequestLineException(data)
		request, data = data.split(b'\n', 1)
		request = request.strip().decode()
		if not request:
			return None
		match = REQUEST.match(request)
		if match is None:
			raise MalformedRequestLineException(request)

		self.method: str = match.group(1)
		self.path: str = match.group(2)
		self.version: str = match.group(3)
		self.payload: HTTPPayload = HTTPPayload(data)

	def __bytes__(self) -> bytes:
		return (
			f"{self.method} {self.path} HTTP/{self.version}\r\n".encode()
			+ bytes(self.payload)
		)


class HTTPResponse:
	def __init__(self, data: bytes) -> None:
		if b'\n' not in data:
			raise MalformedResponseLineException(data)
		request, data = data.split(b'\n', 1)
		request = request.strip().decode()
		if not request:
			return None
		match = RESPONSE.match(request)
		if not match:
			raise MalformedResponseLineException(request)

		self.version: str = match.group(1)
		self.code: str = match.group(2)
		self.message: str = match.group(3)
		self.payload: HTTPPayload = HTTPPayload(data)

	def __bytes__(self) -> bytes:
		return (
			f"HTTP/{self.version} {self.code} {self.message}\r\n".encode()
			+ bytes(self.payload)
		)


##############################   SAMPLE FILTERS   ##############################


def http_response(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:
	
	try:
		req = HTTPResponse(data)


		req.payload.body = replace_flag(logger, req.payload.body, id)

		return bytes(req)
	except Exception as e:
		logger.error(f'{e}')

	return data

def http_request(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:
	try:
		req = HTTPRequest(data)

		return bytes(req)
	except Exception as e:
		logger.error(f'{e}')

	return data


# Log
logger.debug(__file__)
