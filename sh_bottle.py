import logging
import os
from bottle import default_app, route, request, error
from datetime import datetime, timedelta

IP_LIST = dict()
LIFE_TIME = timedelta(minutes=30)
REFRESH_TIME = timedelta(minutes=1)
PREVIOUS_CHECK = datetime.utcnow()
SCRIPT_PATH = os.path.dirname(__file__)
LOG_PATH = os.path.join(SCRIPT_PATH, 'IpLogger.log')
IP_PATH = os.path.join(SCRIPT_PATH, 'iplist.txt')
logging.basicConfig(
    filename=LOG_PATH, level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s')
logging.info('Server started')
STR_APP = 'open-horizon'
STR_VERSION = '1'
PAGE_404_ERROR = 'Ya ain\'t allowed to be here'
PAGE_LOG_STR = '''ATTENTIONThis computer system has been seized
by the United States Secret Service in the interests of
National Security. Your IP has been logged.'''


def load():
    try:
        with open(IP_PATH, 'r') as f:
            t0 = datetime.utcnow()
            for line in f:
                IP_LIST[line] = t0
    except Exception:
        logging.warning('iplist file not found')


def save():
    try:
        with open(IP_PATH, 'w') as f:
            for ip in IP_LIST.keys():
                f.write('{}\n'.format(ip))
    except Exception:
        logging.error('iplist write error')

load()


def deco_version_check(f):
    def wrapper(*args, **kws):
        if not (
                request.GET.get('app', '') == STR_APP and
                request.GET.get('version', '') == STR_VERSION):
            return
        return f()
    return wrapper


def clear_old_records():
    global PREVIOUS_CHECK, IP_LIST
    ips = []
    if IP_LIST:
        t0 = datetime.utcnow()
        if t0 - PREVIOUS_CHECK > REFRESH_TIME:
            PREVIOUS_CHECK = t0
            for ip, t in list(IP_LIST.items()):
                if t0 - t > LIFE_TIME:
                    logging.info('ip removed:{}'.format(IP_LIST.pop(ip, None)))
                else:
                    ips.append(ip)
            save()
        else:
            ips = IP_LIST.keys()
    return ips


@error(404)
def error_404(error):
    return PAGE_404_ERROR


@route('/get', method='GET')
@deco_version_check
def return_ip_list():
    ips = clear_old_records()
    logging.info('ip list request')
    return '\n'.join(ips)


@route('/log', method='GET')
@deco_version_check
def log_client_ip():
    global IP_LIST
    addr = request.headers.get('X-Real-IP')
    IP_LIST[addr] = datetime.utcnow()
    logging.info('ip logged:{}'.format(addr))
    return PAGE_LOG_STR

application = default_app()
