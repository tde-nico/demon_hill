from importlib import import_module, reload

'''
from .log import *
from .settings import *
from .utils import *
from .tables import *
from .submitter import *
from .http import *
from .filters import *
from .tcp_proxy import *
'''

PACKAGE = 'demon_hill'

def load_module(name):
	mdl = import_module(name, package=PACKAGE)
	try:
		if RELOAD:
			reload(mdl)
	except Exception as e:
		if str(e) != "name 'RELOAD' is not defined":
			print(e)
	if "__all__" in mdl.__dict__:
		names = mdl.__dict__["__all__"]
	else:
		names = [x for x in mdl.__dict__ if not x.startswith("_")]
	globals().update({k: getattr(mdl, k) for k in names})


MODULES = [
	'log',
	'settings',
	'utils',
	'tables',
	'http',
	'filters',
	'tcp_proxy',
	'reload',
]

for module in MODULES:
	load_module('.' + module)


