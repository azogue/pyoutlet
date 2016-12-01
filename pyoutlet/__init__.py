# -*- coding: utf-8 -*-
"""
Minimal controler for 433Mhz RF Wireless Power Outlets
FROM:   http://timleland.com/wireless-power-outlets/
        https://github.com/timleland/rfoutlet

"""
import json
import os
from subprocess import check_output, CalledProcessError
import re


def _clean(s):
    return s.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')


basedir = os.path.dirname(os.path.abspath(__file__))
PATH_CODES_OUTLETS = os.path.join(basedir, 'codes_outlets.json')
PATH_SCRIPT_SENDCODE = os.path.join(basedir, 'switch.sh')
OUTPUT_MASK = 'Sending Code: (?P<code>\d{1,8})\. PIN: (?P<pin>\d{1,2})\. Pulse Length: (?P<length>\d{1,4})'

CODES_CONF = json.load(open(PATH_CODES_OUTLETS, 'r'))
PULSE_LENGTH = CODES_CONF['pulse_length']
OUTLETS = CODES_CONF['outlets']
OUTLETS_LABELED = {_clean(v['label']): v for v in OUTLETS}


def _get_code(outlet, operation='off'):
    if type(outlet) is int:
        assert outlet > 0
        code = OUTLETS[outlet - 1][operation]
    elif _clean(outlet) in OUTLETS_LABELED.keys():
        code = OUTLETS_LABELED[_clean(outlet)][operation]
    else:
        try:
            ind = int(outlet) - 1
            assert ind > 0
            code = OUTLETS[ind][operation]
        except ValueError as e:
            print('ValueError finding Outlet CODE: {}'.format(e))
            return None
    return code


def _send_command(outlet, operation='off', verbose=False):
    code = _get_code(outlet, operation)
    if code is None:
        return False
    try:
        out = check_output([PATH_SCRIPT_SENDCODE, str(code)]).decode()
    except CalledProcessError as e:
        if verbose:
            print('CalledProcessError:', e)
        return False
    if verbose:
        print('TURN {} SWITCH "{}" -> \033[0m\033[1m\033[34m{}\033[0m'.format(operation.upper(), outlet, out))
    result_d = re.search(OUTPUT_MASK, out).groupdict()
    return (result_d['length'] == str(PULSE_LENGTH)) and (result_d['code'] == str(code)) and (result_d['pin'] == '0')


def turn_on_outlet(outlet, verbose=False):
    """
    Turn ON an outlet by sending its code for it.

    :param str or int outlet: outlet index (1->X) integer; or outlet str label; or even index = int(outlet).
    :param bool verbose: Print operation info to sys.stdout
    :return: operation ok
    :rtype: bool
    """
    return _send_command(outlet, operation='on', verbose=verbose)


def turn_off_outlet(outlet, verbose=False):
    """
    Turn OFF an outlet by sending its code for it.

    :param str or int outlet: outlet index (1->X) integer; or outlet str label; or even index = int(outlet).
    :param bool verbose: Print operation info to sys.stdout
    :return: operation ok
    :rtype: bool
    """
    return _send_command(outlet, operation='off', verbose=verbose)
