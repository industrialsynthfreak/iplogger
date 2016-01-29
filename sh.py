import sys

if (sys.version_info >= (3, 5)):
	import sh35 as sh
elif (sys.version_info >= (3, 4)):
	import sh34 as sh
else:
	raise SystemExit("You have to update your python")

if __name__ == "__main__":
	sh.IpLoggerServer.run()
