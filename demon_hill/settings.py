import socket, select, threading
import os, sys, re
import logging
import random, string
import requests, datetime

LOG_LEVEL = 'debug'

FROM_ADDR = '0.0.0.0'
LOCALHOST = '127.0.0.1'
TO_ADDR = LOCALHOST

FROM_PORT = 8001
TO_PORT = 8002

SERVER_HISTORY_SIZE = 1024 * 1024
CLIENT_HISTORY_SIZE = 1024 * 1024

AUTO_SET_TABLES = True


FLAG_LEN = 32
FLAG_REGEX = rb'[A-Z0-9]{31}='

REGEX_MASKS = [
	#rb'1\n[a-zA-Z0-9]{3}\n\n5\n2\n[a-zA-Z0-9]*\n3\n0\n2\n',
]

REGEX_MASKS_2 = [
	#rb'filename=".*"',
]


##############################   COLORS   ##############################



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

