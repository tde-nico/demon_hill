from importlib import import_module, reload


PACKAGE = 'demon_hill'

def load_module(name):
	mdl = import_module(name, package=PACKAGE)
	reload(mdl)
	if "__all__" in mdl.__dict__:
		names = mdl.__dict__["__all__"]
	else:
		names = [x for x in mdl.__dict__ if not x.startswith("_")]
	globals().update({k: getattr(mdl, k) for k in names})


MODULES = [
	'log',
	'settings',
	'utils',
	'submitter',
	'http',
	'filters',
	#'client2server',
	'tcp_proxy',
]


for module in MODULES:
	load_module('.' + module)


