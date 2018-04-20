# -*- coding: utf-8 -*-


import redis

from tlutil.caches import rc_cached

from .configs import REDIS_IP, REDIS_PORT


rc = redis.Redis(REDIS_IP, REDIS_PORT)


def _gen_key(pattern, names, args):
    values = args[:len(names)]
    replaces = dict(zip(names, values))
    return pattern.format(**replaces)


def cached(pattern, timeout=0):
    return rc_cached(rc, pattern, timeout)


def delete_cached(name):
    return rc.delete(name)
