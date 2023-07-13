from sys import argv
from os import _exit, getpid
from importlib import import_module, reload
from threading import enumerate



if __name__ == '__main__':
	dh = import_module('demon_hill')

	if len(argv) == 3:
		dh.FROM_PORT = int(argv[1])
		dh.TO_PORT = int(argv[2])

	proxy = dh.TCPProxy(dh.logger, dh.FROM_ADDR, dh.TO_ADDR, dh.FROM_PORT, dh.TO_PORT)
	proxy.start()

	proxy.lock.acquire()
	if not proxy.sock:
		_exit(0)
	proxy.lock.release()

	reload_string = dh.to_rainbow('Reloading Proxy')

	while True:
		try:
			cmd = input()

			if cmd[:1] == 'q':
				proxy.lock.acquire()
				proxy.close()
				proxy.lock.acquire()
				_exit(0)

			elif cmd[:1] == 'r':
				dh.logger.info(reload_string)
				reload(dh)
				tmp_sock = proxy.sock
				proxy.lock.acquire()
				proxy.is_running = False
				proxy.sample_connection()
				proxy.lock.acquire()
				proxy.lock.release()
				proxy = dh.TCPProxy(dh.logger, dh.FROM_ADDR, dh.TO_ADDR, dh.FROM_PORT, dh.TO_PORT, tmp_sock)
				proxy.start()
			
			elif cmd[:1] == 'i':
				dh.logger.info(f'{dh.HIGH_CYAN}PID{dh.END}: {dh.GREEN}{getpid()}{dh.END}')
				dh.logger.info(f'{dh.HIGH_CYAN}Threads{dh.END}: {dh.GREEN}{len(enumerate())}{dh.END}')

		except KeyboardInterrupt:
			proxy.lock.acquire()
			proxy.close()
			proxy.lock.acquire()
			_exit(0)
		except Exception as e:
			dh.logger.error(str(e))

