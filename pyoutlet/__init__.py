# -*- coding: utf-8 -*-
"""
Minimal controler for 433Mhz RF Wireless Power Outlets
FROM:   http://timleland.com/wireless-power-outlets/
        https://github.com/timleland/rfoutlet

"""
from collections import OrderedDict
from io import BytesIO
import json
from jsondiff import diff
import os
from subprocess import check_output, CalledProcessError
import re


__version__ = '0.0.5'

basedir = os.path.dirname(os.path.abspath(__file__))
PATH_CODES_OUTLETS = os.path.join(basedir, 'codes_outlets.json')
PATH_SCRIPT_SENDCODE = os.path.join(basedir, 'switch.sh')
OUTPUT_MASK = 'Sending Code: (?P<code>\d{1,8})\. PIN: (?P<pin>\d{1,2})\. Pulse Length: (?P<length>\d{1,4})'
INDENTATION = 4

TITLE_GENERAL_CONF = 'General config'


#############################
# Switcher Object
#############################
class Switcher(object):
    """
    Object to join configuration and switch methods of PYOUTLETS installation

    """
    path_codes_conf = PATH_CODES_OUTLETS
    _codes_conf = None
    _pulse_length = None
    _outlets = None
    _outlets_labeled = None
    _outlets_state = None

    def __init__(self):
        self._load()

    def __repr__(self):
        msg = ('\n** PYOUTLET JSON config in "{}"\n--> * {}\n'
               .format(self.path_codes_conf,
                       '\n    * '.join(['{:20} -> ON:{}, OFF:{}'.format(d['label'], d['on'], d['off'])
                                        for d in self._outlets])))
        return msg

    def __len__(self):
        return len(self._outlets)

    def __getitem__(self, item):
        return self._outlets[item]

    def _load(self):
        ok_conf, self._codes_conf = self._json_load(self.path_codes_conf, is_path=True)
        assert ok_conf
        self._pulse_length = str(self._codes_conf['pulse_length'])
        self._outlets = self._codes_conf['outlets']
        self._outlets_labeled = {self._clean(v['label']): (i, v) for i, v in enumerate(self._outlets)}
        self._outlets_state = [None] * len(self._outlets)

    @property
    def config_text(self):
        """
        Return the JSON config in indented multi-line text (for printing purposes)

        :return: formatted config text
        :rtype: str

        """
        return json.dumps(self._codes_conf, indent=INDENTATION, ensure_ascii=False)

    @property
    def homebridge_accessories(self):
        """
        Return the outlets config in JSON format for `homebridge-rcswitch-gpiomem`:

        "accessories": [
        {
            "accessory": "RCSwitch",
            "name": "Switch 1",
            "onCode": 4529411,
            "offCode": 4529420,
            "pulseLength": 185
        },
        {
            "accessory": "RCSwitch",
            "name": "Switch 2",
            "onCode": 4529411,
            "offCode": 4529420,
            "pulseLength": 185
        },
        ...]

        :return: JSON config
        :rtype: str

        """
        pulse_length = int(self._pulse_length)
        list_outlets = [{"accessory": "RCSwitch",
                         "name": outlet['label'],
                         "onCode": outlet['on'],
                         "offCode": outlet['off'],
                         "pulseLength": pulse_length} for outlet in self._outlets]
        return json.dumps({"accessories": list_outlets}, indent=INDENTATION, ensure_ascii=False)

    @property
    def outlets_state(self):
        """
        Return list of probable states of outlets (last asigned by pyoutletweb in current session or unknown)

        :return: current states (True|False|None)
        :rtype: list

        """
        return self._outlets_state

    @staticmethod
    def _clean(s):
        """
        Clean label for easy identification

        :param str s:
        :return: clean label
        :rtype: str

        """
        return s.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

    @staticmethod
    def _json_load(path, is_path=True):
        try:
            if is_path:
                return True, json.load(open(path, 'r'))
            return True, json.loads(path)
        except json.JSONDecodeError as e:
            if is_path:
                msg_err = "Can't decode: '{}' --> JSONDecodeError: {}".format(open(path, 'r').read(), e)
            else:
                msg_err = "Can't decode: '{}' --> JSONDecodeError: {}".format(path, e)
            return False, {'error': msg_err}

    #############################
    # RF Send commands
    #############################
    def _send_command(self, outlet, operation='off', verbose=False):
        """
        Send RF command for turn ON or OFF an outlet by name or #

        :param str or int outlet: outlet id
        :param str operation: 'on' or 'off
        :param bool verbose: shows info in stdout
        :return: operation ok
        :rtype: bool

        """
        if type(outlet) is int:
            assert outlet > 0
            ind_outlet = outlet - 1
            code = self._outlets[outlet - 1][operation]
        elif self._clean(outlet) in self._outlets_labeled.keys():
            code = self._outlets_labeled[self._clean(outlet)][1][operation]
            ind_outlet = self._outlets_labeled[self._clean(outlet)][0][operation]
        else:
            try:
                ind_outlet = int(outlet) - 1
                assert ind_outlet > 0
                code = self._outlets[ind_outlet][operation]
            except ValueError as e:
                print('ValueError finding Outlet CODE: {}'.format(e))
                code = None
                ind_outlet = 0

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
        ok = ((result_d['length'] == self._pulse_length) and
              (result_d['code'] == str(code)) and (result_d['pin'] == '0'))

        # set last state:
        if ok:
            turn_off = operation == 'off'
            if self._outlets_state[ind_outlet] is None:
                self._outlets_state[ind_outlet] = not turn_off
            elif self._outlets_state[ind_outlet] and turn_off:
                self._outlets_state[ind_outlet] = False
            elif not self._outlets_state[ind_outlet] and not turn_off:
                self._outlets_state[ind_outlet] = True
        return ok

    def turn_on_outlet(self, outlet, verbose=False):
        """
        Turn ON an outlet by sending its code for it.

        :param str or int outlet: outlet index (1->X) integer; or outlet str label; or even index = int(outlet).
        :param bool verbose: Print operation info to sys.stdout
        :return: operation ok
        :rtype: bool
        """
        return self._send_command(outlet, operation='on', verbose=verbose)

    def turn_off_outlet(self, outlet, verbose=False):
        """
        Turn OFF an outlet by sending its code for it.

        :param str or int outlet: outlet index (1->X) integer; or outlet str label; or even index = int(outlet).
        :param bool verbose: Print operation info to sys.stdout
        :return: operation ok
        :rtype: bool
        """
        return self._send_command(outlet, operation='off', verbose=verbose)

    #############################
    # Flask web config edition
    #############################
    def webeditdata_outlets_config_json(self, data=None):
        """
        * Create configuration data for web editing and check integrity of data:

        Make Ordered dict like:
        ==> [(section_name,
                OrderedDict([(VARIABLE, (VALUE, 'int|text')),
                             (VARIABLE, (VALUE, 'int|text')),
                             ...
                             (VARIABLE, (VALUE, 'int|text'))])),
             (section_name,
                OrderedDict([(VARIABLE, (VALUE, 'int|text')),
                             (VARIABLE, (VALUE, 'int|text')),
                             ...
                             (VARIABLE, (VALUE, 'int|text'))])),
             ...]

        :param dict data: Outlets configuration
        :return: :tuple of (ok, dict_file_for_webform):

        """
        if data is None:
            data = self._codes_conf

        config_entries = OrderedDict()
        config_entries[TITLE_GENERAL_CONF] = OrderedDict()
        config_entries[TITLE_GENERAL_CONF]['pulse_length'] = (data['pulse_length'], 'int')

        ok = True
        for i, outlet in enumerate(data['outlets']):
            key = 'Outlet {}'.format(i + 1)
            config_entries[key] = OrderedDict()
            config_entries[key]['Label'] = (outlet['label'], 'str')
            config_entries[key]['ON Code'] = (outlet['on'], 'int')
            config_entries[key]['OFF Code'] = (outlet['off'], 'int')
            ok = ok and ((type(config_entries[key]['Label'][0]) is str) and
                         (type(config_entries[key]['ON Code'][0]) is int) and
                         (type(config_entries[key]['OFF Code'][0]) is int))
        return ok, config_entries

    @staticmethod
    def _config_json_from_webeditdata(webdata):
        """
        Conversion from webdata ImmutableMultiDict to JSON outlets config dict

        :param ImmutableMultiDict webdata: Outlets configuration in web form
        :return: (ok operation, JSON config dict):
        :rtype: tuple

        """
        webdata = webdata.copy()
        data = {}
        if ('Label' in webdata) and ('ON Code' in webdata) and ('OFF Code' in webdata) and ('pulse_length' in webdata):
            try:
                data['pulse_length'] = int(webdata.poplist('pulse_length')[0])
                data['outlets'] = [{'label': label, 'on': int(on_code), 'off': int(off_code)}
                                   for label, on_code, off_code in zip(webdata.poplist('Label'),
                                                                       webdata.poplist('ON Code'),
                                                                       webdata.poplist('OFF Code'))]
                return True, data
            except ValueError:
                return False, data
        else:
            return False, webdata

    def _process_config_changes(self, dict_config_new, dict_config_before):
        """
        Process changes in web editor of ENERPI SENSORS JSON File

        :param dict_config_new: New JSON data (from web post or uploaded file)
        :param dict_config_before: original config dict of dicts
                                (like the one 'web_edit_enerpi_sensors_json' returns)
        :return: (dict: alert message, OrderedDict: updated dict_config))
        :rtype: tuple

        """
        diff_json = diff(dict_config_before, dict_config_new)
        ok_new, _ = self.webeditdata_outlets_config_json(dict_config_new)
        if diff_json and ok_new:
            with open(self.path_codes_conf, 'w') as f:
                json.dump(dict_config_new, f, indent=INDENTATION, ensure_ascii=False)
            self._load()
            str_cambios = ('OUTLETS Config changes:<br>{}<br> New configuration SAVED!'
                           .format('JSON DIFF- <strong>"{}"</strong>'.format(diff_json)))
            alerta = {'alert_type': 'warning', 'texto_alerta': str_cambios}
        elif ok_new:
            alerta = {'alert_type': 'warning', 'texto_alerta': 'No changes in new JSON config...'}
        else:
            dict_config_new = dict_config_before
            alerta = {'alert_type': 'danger', 'texto_alerta': 'NEW JSON FILE NOT VALID!! FIX IT, PLEASE'}
        return alerta, dict_config_new

    def webconfig_edition_data(self, d_edition_form):
        """
        Method for validate and save changes on JSON outlets configuration.
        It returns data for jinja2 templates:
            (alert message, config data for web user edition)

        :param d_edition_form: request.form dict for config POST requests
        :return: (dict: alert message, OrderedDict: dict_config for jinja2 templates))
        :rtype: tuple

        """
        ok_form, dict_config_new = self._config_json_from_webeditdata(d_edition_form)
        if not ok_form:
            alerta = {'alert_type': 'danger', 'texto_alerta': 'NEW JSON VALUES NOT VALID!!'}
            dict_config_new = self._codes_conf
        else:
            alerta, dict_config_new = self._process_config_changes(dict_config_new, self._codes_conf)
        ok_data, config_webdata = self.webeditdata_outlets_config_json(dict_config_new)
        if not ok_data:
            alerta = {'alert_type': 'danger', 'texto_alerta': 'BAD CONFIG: {}'.format(config_webdata)}
        return alerta, config_webdata

    def check_uploaded_file(self, f_obj):
        """
        Check uploaded JSON configuration file and save it if correct. Return dict for web alert

        :param werkzeug.datastructures.FileStorage f_obj: uploaded file object
        :return: web alert
        :rtype: dict

        """
        # file_name, file_extension = os.path.splitext(f_obj.filename)
        fmem = BytesIO()
        f_obj.save(fmem)
        fmem.seek(0)
        ok, json_config = self._json_load(fmem.read().decode(), is_path=False)
        if ok:
            alerta, config_webdata = self._process_config_changes(json_config, self._codes_conf)
            if not alerta:
                alerta = {'alert_type': 'info', 'texto_alerta': 'No changes in JSON CONFIG. Nothing to do...'}
        else:
            alerta = {'alert_type': 'danger', 'texto_alerta': 'BAD UPLOADED JSON FILE: {}'.format(json_config['error'])}
        return alerta
