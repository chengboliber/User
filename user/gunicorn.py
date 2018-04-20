# -*- coding: utf-8 -*-

import os
import sys

_basedir = os.path.abspath(os.path.dirname(__file__))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

from user.configs import SERVER_IP, SERVER_PORT, DEBUG


bind = '%s:%s' % (SERVER_IP, SERVER_PORT)
backlog = 2048

workers = 4
worker_class = 'gevent'
worker_connections = 1000
max_requests = 10000
timeout = 10

debug = DEBUG
daemon = False
