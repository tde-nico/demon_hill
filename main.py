from sys import argv
from os import _exit, getpid
from importlib import import_module, reload
from threading import enumerate


if __name__ == '__main__':
	dh = import_module('demon_hill')

	if len(argv) == 3:
		dh.FROM_PORT = int(argv[1])
		dh.TO_PORT = int(argv[2])

	reload_string = dh.to_rainbow('Reloading Proxy')

	proxy = dh.TCPProxy(dh.logger, dh.FROM_ADDR, dh.TO_ADDR, dh.FROM_PORT, dh.TO_PORT)
	proxy.start()

	proxy.lock.acquire()
	if not proxy.sock:
		_exit(0)
	proxy.lock.release()

	if dh.AUTO_SET_TABLES:
		dh.enable_forwarding(dh.logger)

	while True:
		try:
			cmd = input()

			if cmd[:1] == 'q': # Quit
				proxy.exit()

			elif cmd[:1] == 'r': # Reload
				dh.logger.info(reload_string)
				dh.RELOAD = True
				reload(dh)
				tmp_sock = proxy.sock
				proxy.lock.acquire()
				proxy.is_running = False
				proxy.sample_connection()
				proxy.lock.acquire()
				proxy.lock.release()
				proxy = dh.TCPProxy(dh.logger, dh.FROM_ADDR, dh.TO_ADDR, dh.FROM_PORT, dh.TO_PORT, tmp_sock)
				proxy.start()
			
			elif cmd[:1] == 'i': # Info
				dh.logger.info(f'{dh.HIGH_CYAN}PID{dh.END}: {dh.GREEN}{getpid()}{dh.END}')
				dh.logger.info(f'{dh.HIGH_CYAN}Threads{dh.END}: {dh.GREEN}{len(enumerate())}{dh.END}')

			elif cmd[:1] == 'f': # Forwarding
				dh.enable_forwarding(dh.logger)
			elif cmd[:1] == 'd': # Disable Forwarding
				dh.disable_forwarding(dh.logger)

			elif cmd[:1] == '+': # increases logs
				dh.loglevel_up()
			elif cmd[:1] == '-': # decreases logs
				dh.loglevel_down()

		except KeyboardInterrupt:
			proxy.exit()
		except Exception as e:
			dh.logger.error(str(e))

