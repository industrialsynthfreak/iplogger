import logging
import os
from bottle import default_app, route, request, error
from datetime import datetime, timedelta

IP_LIST = dict()
_PREVIOUS_CHECK = datetime.utcnow()
LIFE_TIME = timedelta(minutes=30)
REFRESH_TIME = timedelta(minutes=1)
SCRIPT_PATH = os.path.dirname(__file__)
LOG_PATH = os.path.join(SCRIPT_PATH, 'IpLogger.log')
IP_PATH = os.path.join(SCRIPT_PATH, 'iplist.txt')
APP_STR = 'open-horizon'
VERSION_STR = '1'
PAGE_404_STR = 'Ya ain\'t allowed to be here'
PAGE_LOG_STR = '''ATTENTIONThis computer system has been seized
by the United States Secret Service in the interests of
National Security. Your IP has been logged.'''
PAGE_GET_HEADER_STR = ''
PAGE_BAD_INPUT_STR = 'You bad!'


def load():
    try:
        with open(IP_PATH, 'r') as f:
            t0 = datetime.utcnow()
            for line in f:
                ip, port = line.split(':')
                IP_LIST[ip] = (t0, int(port))
    except Exception:
        logging.warning('iplist file not found')


def save():
    try:
        with open(IP_PATH, 'w') as f:
            for ip, args in list(IP_LIST.items()):
                t, port = args
                f.write('{}:{}\n'.format(ip, port))
    except Exception:
        logging.error('iplist write error')


def deco_args_check(f):
    def wrapper(*args, **kws):
        if not (
                request.GET.get('app', '') == APP_STR and
                request.GET.get('version', '') == VERSION_STR):
            return bad_input()
        return f(*args, **kws)
    return wrapper


def clear_old_records():
    global _PREVIOUS_CHECK, IP_LIST
    ips = []
    s = '{}:{}'
    if IP_LIST:
        t0 = datetime.utcnow()
        if t0 - _PREVIOUS_CHECK > REFRESH_TIME:
            _PREVIOUS_CHECK = t0
            for ip, args in list(IP_LIST.items()):
                t, port = args
                if t0 - t > LIFE_TIME:
                    logging.info('ip removed:{}'.format(IP_LIST.pop(ip, None)))
                else:
                    ips.append(s.format(ip, port))
            save()
        else:
            ips = [s.format(ip, args[1]) for ip, args in IP_LIST.items()]
    return ips


def bad_input():
    return PAGE_BAD_INPUT_STR


@error(404)
def error_404(error):
    return PAGE_404_STR


@route('/get', method='GET')
@deco_args_check
def return_ip_list():
    ips = clear_old_records()
    logging.info('ip list request')
    return PAGE_GET_HEADER_STR + '\n'.join(ips)


@route('/log', method='GET')
@deco_args_check
def log_client_ip():
    global IP_LIST
    try:
        port = int(request.GET.get('port'))
        if not(0 < port < 2**16):
            raise ValueError
    except Exception:
        return bad_input()
    addr = request.headers.get('X-Real-IP')
    IP_LIST[addr] = (datetime.utcnow(), port)
    logging.info('ip logged:{}:{}'.format(addr, port))
    return PAGE_LOG_STR

logging.basicConfig(
    filename=LOG_PATH, level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s')
logging.info('Server started')
load()
application = default_app()
