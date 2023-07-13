from .settings import *
from .log import *


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


# Log
logger.debug(__file__)
