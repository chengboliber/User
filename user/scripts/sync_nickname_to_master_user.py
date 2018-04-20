# -*- coding: utf-8 -*-
'''
将用户昵称同步到主播用户表
'''

import os
import sys
import time
from datetime import datetime, timedelta

_basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

from user import users as users_service
from user.users import models

from tlclient.zhibo.room import RoomClient
room_client = RoomClient()

def sync_nickname():
    update_count = 0
    page_limit = 10000
    for i in range(100):
        sql = '''
            SELECT user_id FROM master_user
            WHERE nickname is null
            ORDER BY user_id ASC
            LIMIT {page_offset}, {page_limit}
            '''
        page_offset = i * page_limit
        sql = sql.format(page_offset=page_offset, page_limit=page_limit)
        ret = models.exec_query(sql, islist=True)
        if not ret:
            break
        for user in ret:
            user_id = user['user_id']
            user_info = users_service.get_user_info(user_id)
            if not user_info:
                continue
            nickname = user_info['nickname']
            rooms = room_client.list(user_id=user_id)
            if not nickname and not rooms:
                continue
            if rooms:
                room_id = rooms[0]['id']
            else:
                room_id = None
            master_user_table = models.get_master_user_table()
            update_sql = master_user_table.update(master_user_table.c.user_id == user_id)\
                            .values(nickname=nickname, room_id=room_id)
            models.exec_change(*[update_sql])
            update_count += 1

    print u'同步了 %s 个主播用户' % update_count


if __name__ == '__main__':
    sync_nickname()
    print 'DONE'
