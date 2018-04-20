# -*- coding: utf-8 -*-

from . import constants as USER
from ..core import rc


def incr_user_id():
    key = USER.REDIS_USER_ID
    if not rc.exists(key):
        rc.set(key, 10000)
    return rc.incr(key)


def incr_user_count(user_id, count_type, amount=1):
    name = USER.REDIS_USER_COUNT.format(user_id=user_id)
    return rc.hincrby(name, count_type, amount)


def decr_user_count(user_id, count_type):
    name = USER.REDIS_USER_COUNT.format(user_id=user_id)
    if rc.exists(name):
        return rc.hincrby(name, count_type, -1)


def get_user_count(user_id):
    name = USER.REDIS_USER_COUNT.format(user_id=user_id)
    return rc.hgetall(name)


def set_user_count(user_id, count_type, amount):
    ''' 设置用户的关注与粉丝数（用于修复脚本） '''
    name = USER.REDIS_USER_COUNT.format(user_id=user_id)
    return rc.hset(name, count_type, amount)