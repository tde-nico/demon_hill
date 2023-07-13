from .settings import *


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


# Log
logger.debug(__file__)
