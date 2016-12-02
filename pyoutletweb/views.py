# -*- coding: utf-8 -*-
"""
Minimal web API controler for 433Mhz RF Wireless Power Outlets

Main view

INSPIRED FROM:
    http://timleland.com/wireless-power-outlets/
    https://github.com/timleland/rfoutlet

"""
from flask import request, redirect, url_for, render_template, flash, send_file, abort
import os
from pyoutletweb import app, VERBOSE
from pyoutlet import Switcher, TITLE_GENERAL_CONF


#############################
# Outlet control
#############################
switch = Switcher()


def _switch_outlet(outlet_number, turn_off=True):
    global switch
    if turn_off:
        ok = switch.turn_off_outlet(outlet_number, VERBOSE)
    else:
        ok = switch.turn_on_outlet(outlet_number, VERBOSE)
    # Alert:
    operation = 'OFF' if turn_off else 'ON'
    if ok:
        msg = ('Outlet <strong>{}</strong> (<strong>{}</strong>) switched <strong>{}</strong>'
               .format(outlet_number, switch[outlet_number - 1]['label'], operation))
        alert_t = 'success'
    else:
        msg = ('ERROR trying to switch {} Outlet <strong>{}</strong> (<strong>{}</strong>)'
               .format(operation, outlet_number, switch[outlet_number - 1]['label']))
        alert_t = 'danger'
    return msg, alert_t


#############################
# Operation Routes
#############################
@app.route("/", methods=['GET'])
def index():
    """
    Index page with ON/OFF buttons for all outlets

    """
    global switch
    return render_template('outlets_control.html', outlets=switch, outlets_state=switch.outlets_state)


@app.route("/switch/<operation>/<outlet_number>", methods=['GET'])
def switch_outlet(operation, outlet_number):
    """
    Turn ON or OFF an outlet by its number.

    :param str operation: 'ON' / 'OFF'
    :param int outlet_number: # of outlet (1 -> X)

    """
    if operation.lower() not in ['on', 'off']:
        return abort(500, 'BAD OUTLET OPERATION -> "{}" (Outlet={})'.format(operation, outlet_number))
    outlet_number = int(outlet_number)
    msg, alert_t = _switch_outlet(outlet_number, operation.lower() == 'off')
    flash(msg, alert_t)
    return redirect(url_for('index'), code=307)


#############################
# Config. handling routes
#############################
@app.route('/config/download', methods=['GET'])
def download_config():
    """
    JSON configuration file download

    """
    global switch
    flash('<strong>JSON config</strong> file downladed!!', 'success')
    if 'as_attachment' in request.args:
        return send_file(switch.path_codes_conf, as_attachment=True,
                         attachment_filename=os.path.basename(switch.path_codes_conf))
    return send_file(switch.path_codes_conf, as_attachment=False)


@app.route('/config/upload', methods=['POST'])
def uploadfile():
    """
    POST method for interesting config files upload & replacement

    """
    global switch
    f = request.files['file']
    alerta = switch.check_uploaded_file(f)
    if alerta:
        flash(alerta['texto_alerta'], alerta['alert_type'])
    else:
        flash('<strong>JSON config</strong> file uploaded!!', 'success')
    return redirect(url_for('config_editor'))


@app.route("/config", methods=['GET', 'POST'])
def config_editor():
    """
    General configuration webpage for view/edit/download/upload the JSON configuration of pyoutlets

    """
    global switch
    if request.method == 'GET':
        ok, config_webdata = switch.webeditdata_outlets_config_json()
        if not ok:
            flash('<strong>BAD JSON</strong> configuration!!', 'danger')
    else:  # POST from web form
        assert request.form
        alerta, config_webdata = switch.webconfig_edition_data(request.form)
        if alerta:
            flash(alerta['texto_alerta'], alerta['alert_type'])
    return render_template('outlets_editor.html',
                           file_lines=switch.config_text,
                           section_genconf=TITLE_GENERAL_CONF,
                           dict_config_content=config_webdata,
                           homebridge_info=switch.homebridge_accessories,
                           abspath=switch.path_codes_conf)
