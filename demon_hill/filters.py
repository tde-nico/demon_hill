from .settings import *
from .utils import *
from .log import *
from .http import *



def custom_filter(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:

	# write here

	return data


def info_filter(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:
	logger.info(data)
	return data


def regex_filter(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:
	for exclusion in REGEX_MASKS:
		if re.search(exclusion, client_history):
			data = replace_flag(logger, data, id)
			break
	return data





SERVER_FILTERS = [
	regex_filter,
	# http_response,
	# custom_filter,
	# info_filter,
]

CLIENT_FILTERS = [
	# custom_filter,
	# info_filter,
]


# Log
logger.debug(__file__)
