import socket, select, threading
import os, sys, re
import logging
import random, string
import requests, datetime
import ssl

LOG_LEVEL = 'debug'

# IPv6
IPV6 = False
if IPV6:
	INADDR_ANY = '::'
	LOCALHOST = '::1'
else:
	INADDR_ANY = '0.0.0.0'
	LOCALHOST = '127.0.0.1'


# Addrs
FROM_ADDR = INADDR_ANY
TO_ADDR = LOCALHOST

# Ports
FROM_PORT = 1336
TO_PORT = 1337

# SSL
SSL = False
SSL_KEYFILE = "./server-key.pem"
SSL_CERTFILE = "./server-cert.pem"
SSL_CA_CERT = "./ca-cert.pem"

# Auto forwarding
AUTO_SET_TABLES = True


# Max history
SERVER_HISTORY_SIZE = 1024 * 1024
CLIENT_HISTORY_SIZE = 1024 * 1024


# Flag
FLAG_LEN = 32
FLAG_REGEX = rb'[A-Z0-9]{31}='


# Masks
REGEX_MASKS = [
]

REGEX_MASKS_2 = [
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

