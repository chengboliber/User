# -*- coding: utf-8 -*-
import random

from tlutil.helpers import int2ip
from tlutil.timeutil import stamp_to_ct

from users import caches as user_caches

range_list = [ 
    ((1, 10),      (0, 2)),
    ((11, 20),     (2, 4)),
    ((21, 30),     (4, 6)),
    ((31, 40),     (6, 8)),
    ((41, 50),     (8, 10)),
    ((51, 60),     (10, 12)),
    ((61, 70),     (12, 14)),
    ((71, 80),     (14, 16)),
    ((81, 90),     (16, 18)),
    ((91, 100),    (18, 20)),
    ((101, 300),   (11, 13)),
    ((301, 600),   (9, 11)),
    ((601, 1000),  (5, 7)),
    ((1001, 1400), (3, 5)),
    ((1401, 2000), (0, 2)),
]

def get_range(fans_count):
    for ((a,b),c) in range_list:
        if a <= fans_count <= b:
            return c

def gen_vfans_count(fans_count):
    if fans_count >= 2000:
        return 0
    rs = get_range(fans_count)
    if not rs:
        return 0
    (start, end) = rs
    return random.randint(start, end)


def make_user_info(user_info):
    if not user_info.get('username'):
        user_info['username'] = u'玩家%d' % user_info['user_id']
    if not user_info.get('nickname'):
        user_info['nickname'] = u'玩家%d' % user_info['user_id']
    if 'password' in user_info:
        user_info.pop('password')
    if user_info.get('birthday'):
        user_info['birthday'] = user_info['birthday'].strftime('%Y-%m-%d')
    user_info['user_ip'] = int2ip(user_info['user_ip'])
    user_info['create_time'] = stamp_to_ct(user_info['create_time'])
    user_info['update_time'] = stamp_to_ct(user_info['update_time'])
    # 关注与粉丝数
    user_info['count'] = {'fans_count': 0, 'follow_count': 0}
    count = user_caches.get_user_count(user_info['user_id'])
    user_info['count'].update(count)
    return user_info
