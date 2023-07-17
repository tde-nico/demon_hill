from .settings import *
from .utils import *
from .log import *
from .http import *



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
	#regex_filter,
	http_response,
]

CLIENT_FILTERS = [
]


# Log
logger.debug(__file__)
