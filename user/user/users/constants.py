# -*- coding: utf-8 -*-

from ..configs import DB_URI


DB_ECHO = False
DB_USER_URI = '%s/tl_user' % (DB_URI)
DB_POOL_SIZE = 100
DB_POOL_RECYCLE = 7200

REDIS_USER_ID = 'RC:user'

REDIS_USER_COUNT = 'tl:user:count:{user_id}'
USER_FOLLOW_COUNT = 'follow_count'
USER_FANS_COUNT = 'fans_count'


DB_USER_SHARD_NUM = 1000000
DB_USER_RELATION_SHARD_NUM = 100000
DB_DEVICE_SHARD_MOD = 100
DB_USERNAME_SHARD_MOD = 100
DB_EMAIL_SHARD_MOD = 10
DB_MOBILE_SHARD_MOD = 10
