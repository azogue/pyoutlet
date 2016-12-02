# -*- coding: utf-8 -*-
"""
Minimal web API controler for 433Mhz RF Wireless Power Outlets

INSPIRED FROM:
    http://timleland.com/wireless-power-outlets/
    https://github.com/timleland/rfoutlet

"""
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.routing import Rule
import jinja2
import os
# noinspection PyUnresolvedReferences
from pyoutlet import __version__


#############################
# Flask application
#############################
VERBOSE = False
PREFIX_WEB = '/outlets'
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

# noinspection PyUnresolvedReferences,PyPep8
from pyoutletweb import views
