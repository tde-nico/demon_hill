from .settings import *
from .log import *
from os import system, getuid


IP_INTERFACE = "eth0"
OUT_BLOCK = " 1>/dev/null"
ERROR_BLOCK = " 2>/dev/null"
IP_PREROUTING = "iptables {} " + f"PREROUTING -t nat -i {IP_INTERFACE} -p tcp --dport {TO_PORT} -j DNAT --to-destination :{FROM_PORT}"
IP_FORWARD = "iptables {} " + f"FORWARD -i {IP_INTERFACE} -p tcp --dport {FROM_PORT} -j ACCEPT"

IP_PREROUTING += ERROR_BLOCK + OUT_BLOCK
IP_FORWARD += ERROR_BLOCK + OUT_BLOCK


def is_routing():
	return system(IP_PREROUTING.format("-C"))


def modify_forwarding(cmd:str, logger:logging.Logger=None) -> bool:
	if getuid() != 0:
		logger.error(f"Need Root to Modify Routing")
		return True
	ret = system(IP_PREROUTING.format(cmd))
	if ret and logger:
		logger.error(f"Prerouting Error {HIGH_RED}{ret}{END}")
		return True
	ret = system(IP_FORWARD.format(cmd))
	if ret and logger:
		logger.error(f"Forward Error {HIGH_RED}{ret}{END}")
		return True
	return False


def enable_forwarding(logger:logging.Logger=None):
	if is_routing():
		if modify_forwarding("-A", logger):
			return
		logger.info(f"{HIGH_GREEN}Routing Enabled {HIGH_CYAN}{TO_PORT} -> {FROM_PORT}{END}")
	else:
		logger.info(f"{HIGH_CYAN}Routing Already Enabled {HIGH_GREEN}{TO_PORT} -> {FROM_PORT}{END}")


def disable_forwarding(logger:logging.Logger=None):
	if not is_routing():
		if modify_forwarding("-D", logger):
			return
		logger.info(f"{HIGH_RED}Routing Disabled {YELLOW}{TO_PORT} -> {FROM_PORT}{END}")
	else:
		logger.info(f"{YELLOW}Routing Already Disabled {HIGH_RED}{TO_PORT} -> {FROM_PORT}{END}")


# Log
logger.debug(__file__)
