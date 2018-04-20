# -*- coding: utf-8 -*-

import os
import logging
import traceback
from os.path import dirname, abspath

from functools import wraps

from flask import current_app
from voluptuous import MultipleInvalid

from tlutil import statsd
from tlutil import factory
from tlutil.json import jsonify
from tlutil.middlewares import StatsdMiddleware
from tlutil.errors import AppError, ErrArgs
from ..configs import ENABLE_STATSD, STATSD_HOST


def create_app(settings_override=None):
    app_name = dirname(dirname(abspath(__file__))).split(os.sep)[-1]
    app = factory.create_app(app_name, __name__, __path__, settings_override)

    if ENABLE_STATSD:
        client = statsd.Client(STATSD_HOST)
        app.wsgi_app = StatsdMiddleware(app, app_name, client)

    app.errorhandler(MultipleInvalid)(on_args_error)
    app.errorhandler(AppError)(on_app_error)

    return app


def route(bp, *args, **kwargs):

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            sc = 200
            rv = f(*args, **kwargs)
            if isinstance(rv, tuple):
                sc = rv[1]
                rv = rv[0]
            return jsonify(rv), sc
        return f

    return decorator


def on_app_error(e):
    if current_app.debug:
        traceback.print_exc()
    data = dict(code=e.code, message=e.message)
    return jsonify(data), e.status_code


def on_args_error(e):
    if not current_app.debug:
        logging.debug(traceback.format_exc())
    return on_app_error(ErrArgs)
