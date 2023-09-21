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


def change_loglevel(direction):
	global levels, log_level, logger
	levels_values = list(levels.values())
	levels_labels = list(levels.keys())
	current_level_index = levels_values.index(log_level)
	current_level = levels_labels[current_level_index]
	if direction > 0:
		if current_level_index < len(levels_values) - 1:
			current_level_index += direction
	else:
		if current_level_index > 0:
			current_level_index += direction
	new_level = levels_values[current_level_index]
	new_level_label = levels_labels[current_level_index]
	logger.critical(f"{HIGH_CYAN}{current_level}{END} -> {GREEN}{new_level_label}{END}")
	log_level = new_level
	logger.setLevel(log_level)


def loglevel_up():
	change_loglevel(-1)


def loglevel_down():
	change_loglevel(+1)


# Log
logger.debug(__file__)
