# -*- coding: utf-8 -*-
"""
Minimal web API controler for 433Mhz RF Wireless Power Outlets

INSPIRED FROM:
    http://timleland.com/wireless-power-outlets/
    https://github.com/timleland/rfoutlet

"""
from pyoutletweb import app, VERBOSE


DEBUG = False
FLASK_WEBSERVER_PORT = 7777


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
