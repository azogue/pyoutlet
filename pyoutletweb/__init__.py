# -*- coding: utf-8 -*-
"""
Minimal web API controler for 433Mhz RF Wireless Power Outlets

INSPIRED FROM:
    http://timleland.com/wireless-power-outlets/
    https://github.com/timleland/rfoutlet

"""
from flask import Flask, render_template, redirect, url_for, abort, flash
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.routing import Rule
import jinja2
import os
# noinspection PyUnresolvedReferences
from pyoutlet import turn_on_outlet, turn_off_outlet, OUTLETS, __version__


VERBOSE = False
DEBUG = False

#############################
# Flask application
#############################
PREFIX_WEB = '/outlets'
FLASK_WEBSERVER_PORT = 7777
basedir = os.path.dirname(os.path.abspath(__file__))

# FLASK APP
app = Flask(__name__, static_path=PREFIX_WEB + '/static')
app.url_rule_class = lambda path, **options: Rule(PREFIX_WEB + path, **options)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.cache = {}
app.jinja_loader = jinja2.FileSystemLoader(os.path.join(basedir, 'templates'))

# Forms protection
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.urandom(24)

# wsgi
app.wsgi_app = ProxyFix(app.wsgi_app)


#############################
# Outlet control
#############################
# Probable outlet states (last asigned by pyoutletweb in current session or unknown):
outlets_state = [None] * len(OUTLETS)


def _switch_outlet(outlet_number, turn_off=True):
    if turn_off:
        ok = turn_off_outlet(outlet_number, VERBOSE)
    else:
        ok = turn_on_outlet(outlet_number, VERBOSE)
    # set last state:
    if ok:
        global outlets_state
        assert outlet_number > 0
        if outlets_state[outlet_number - 1] is None:
            outlets_state[outlet_number - 1] = not turn_off
        elif outlets_state[outlet_number - 1] and turn_off:
            outlets_state[outlet_number - 1] = False
        elif not outlets_state[outlet_number - 1] and not turn_off:
            outlets_state[outlet_number - 1] = True
    return ok


#############################
# ROUTES
#############################
@app.route("/", methods=['GET'])
def index():
    """
    Index page with ON/OFF buttons for all outlets

    """
    global outlets_state
    return render_template('outlets.html', outlets=OUTLETS, outlets_state=outlets_state)


@app.route("/<operation>/<outlet_number>", methods=['GET'])
def switch_outlet(operation, outlet_number):
    """
    Turn ON or OFF an outlet by its number.

    :param str operation: 'ON' / 'OFF'
    :param int outlet_number: # of outlet (1 -> X)

    """
    if operation.lower() not in ['on', 'off']:
        return abort(500, 'BAD OUTLET OPERATION -> "{}" (Outlet={})'.format(operation, outlet_number))
    outlet_number = int(outlet_number)
    ok = _switch_outlet(outlet_number, operation.lower() == 'off')
    if ok:
        msg = ('Outlet <strong>{}</strong> (<strong>{}</strong>) switched <strong>{}</strong>'
               .format(outlet_number, OUTLETS[outlet_number - 1]['label'], operation.upper()))
        alert_t = 'success'
    else:
        msg = ('ERROR trying to switch {} Outlet <strong>{}</strong> (<strong>{}</strong>)'
               .format(operation.upper(), outlet_number, OUTLETS[outlet_number - 1]['label']))
        alert_t = 'danger'
    flash(msg, alert_t)
    return redirect(url_for('index'), code=307)


#############################
# RUN MANUAL SERVER
#############################
def main_runweb():
    """
    Flask webserver

    """
    if VERBOSE:
        print('EJECUTANDO FLASK WSGI A MANO en P:{}!'.format(FLASK_WEBSERVER_PORT))
    app.run(host="0.0.0.0", port=FLASK_WEBSERVER_PORT, processes=1, threaded=False, debug=DEBUG)


if __name__ == "__main__":
    main_runweb()
