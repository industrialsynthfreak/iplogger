import asyncio
import os
import re
import logging

from datetime import datetime, timedelta

__version__ = '0.2'


class IpLoggerServer:
	__ip_last_time_checked = datetime.utcnow()
	ipdb = dict()
	addr = '127.0.0.1'
	port = 8080
	kill_time = timedelta(minutes=30)
	refresh_rate = timedelta(seconds=60)
	data_filepath = os.path.join(os.path.dirname(__file__), 'ipdata.txt')
	log_filepath = os.path.join(os.path.dirname(__file__), 'IpLogger.log')
	ip_get_view = '/get'
	ip_log_view = '/log'

	@classmethod
	@asyncio.coroutine
	def __log_ip(cls, reader, writer):
		data = yield from reader.read(100)
		addr = writer.get_extra_info('peername')[0]
		writer.write('HTTP/1.0 200 OK\r\n'.encode())
		writer.write('Content-Type: text/html\r\n\r\n'.encode())
		logging.info('connection accepted: {}'.format(addr))
		view = data.decode().split()[1]
		time = datetime.utcnow()
		if view == cls.ip_get_view:
			if time - cls.__ip_last_time_checked > cls.refresh_rate:
				cls.__ip_last_time_checked = time
				yield from cls.__ip_time_check()
			writer.write(';'.join(cls.ipdb.keys()).encode('latin-1'))
			logging.info('data sent')
		elif view == cls.ip_log_view:
			cls.ipdb[addr] = time
			logging.info('ip logged')
		else:
			pass
		writer.close()

	@classmethod
	@asyncio.coroutine
	def __ip_time_check(cls):
		if not cls.ipdb:
			return
		for ip, v in list(cls.ipdb.items()):
			if datetime.utcnow() - v > cls.kill_time:
				logging.info('ip removed: {}'.format(cls.ipdb.pop(ip, None)))

	@classmethod
	def __stop(cls, loop):
		cls.save()
		loop.close()
		logging.info('server terminated.')
		logging.shutdown()

	@classmethod
	def save(cls):
		try:
			with open(cls.data_filepath, 'wb') as f:
				f.write('\n'.join(cls.ipdb.keys()).encode())
		except Exception:
			logging.warning('unable to write to a data file')

	@classmethod
	def load(cls):
		try:
			with open(cls.data_filepath, 'rb') as f:
				for line in f:
					cls.ipdb[line.decode()] = datetime.utcnow()
		except Exception:
			logging.warning('ipdata file not found')

	@classmethod
	def run(cls):
		logging.basicConfig(
			filename=cls.log_filepath, level=logging.INFO,
			format='%(asctime)s %(levelname)s %(message)s')
		logging.info('Server started: {}:{}'.format(cls.addr, cls.port))
		cls.load()
		loop = asyncio.get_event_loop()
		tasks = asyncio.gather(
			cls.__ip_time_check(),
			asyncio.start_server(cls.__log_ip, cls.addr, cls.port, loop=loop))
		try:
			loop.run_until_complete(tasks)
			loop.run_forever()
		except (KeyboardInterrupt, SystemExit):
			pass
		cls.__stop(loop)


if __name__ == "__main__":
	IpLoggerServer.run()
