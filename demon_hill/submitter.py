from .settings import *
from .log import *


SUBMITTER_ADDR = '192.168.1.230'
SUBMITTER_PORT = '5555'
SUBMITTER_URL = f'http://{SUBMITTER_ADDR}:{SUBMITTER_PORT}'
API_TOKEN = 'custom_token'
EXPLOIT_NAME = 'Proxy_Mirror'


class MirrorSubmit(threading.Thread):
	def __init__(self, logger:logging.Logger, flags):
		super(MirrorSubmit, self).__init__()
		self.logger = logger
		self.flags = flags
	
	def run(self):
		try:
			self.logger.info(f'Got {GREEN}{len(self.flags)}{END} flags with {BLUE}Mirror Attack{END} from {TO_ADDR}')
			t_stamp = datetime.datetime.now().replace(microsecond=0).isoformat(sep=' ')
			msg = {
				'username': 'Mirror Proxy',
				'flags': [{
					'flag': flag.decode(),
					'exploit_name': EXPLOIT_NAME,
					'team_ip': TO_ADDR,
					'time': t_stamp
				} for flag in self.flags]
			}
			r = requests.post(SUBMITTER_URL + '/api/upload_flags',
				headers={'X-Auth-Token': API_TOKEN},
				json=msg)
			self.logger.info(f'Submitted {GREEN}{len(self.flags)}{END} with {CYAN if r.status_code < 300 else HIGH_RED}{r.status_code}{END} status')
		except Exception as e:
			self.logger.error(f'{e}')


def mirror_filter(logger:logging.Logger, data:bytes, server_history:bytes, client_history:bytes, id:int) -> bytes:
	flags = set(re.findall(FLAG_REGEX, data))
	if flags:
		submit = MirrorSubmit(logger, flags)
		submit.start()
	return data


# Log
logger.debug(__file__)
