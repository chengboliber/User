# -*- coding: utf-8 -*-
'''
给昵称建索引
处理改版前的用户数据，建索引，并处理重复昵称
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

def treat_nickname_index(table_name):
    page_limit = 10000
    for i in range(100):
        sql = '''
            SELECT user_id, nickname FROM {table_name}
            ORDER BY user_id ASC
            LIMIT {page_offset}, {page_limit}
            '''
        page_offset = i * page_limit
        sql = sql.format(table_name=table_name, page_offset=page_offset, page_limit=page_limit)
        ret = models.exec_query(sql, islist=True)
        if not ret:
            break
        for user in ret:
            nickname = user['nickname']
            if not nickname:
                continue
            user_id = users_service.get_user_id_by_nickname(nickname)

            is_write_nickname_index = False
            sqls = []
            # 昵称不存在：写入索引表
            if not user_id:
                is_write_nickname_index = True
            # 昵称存在：是本人，不处理；不是本人，则加上 user_id 后写入索引表
            else:
                if user_id != user['user_id']:
                    nickname = '%s%s' % (nickname[:12], user['user_id'])
                    is_write_nickname_index = True
                    print '[repetition] %s:%s' % (user['nickname'], user_id)
                    print '[repetition] %s:%s' % (nickname, user['user_id'])
                    # 更新用户表中的昵称字段
                    user_table = models.get_user_info_table(user['user_id'])
                    update_sql = user_table.update(user_table.c.user_id == user['user_id'])\
                                        .values(nickname=nickname)
                    sqls.append(update_sql)

            if is_write_nickname_index:
                nickname_index_table = models.get_nickname_index_table(nickname.lower())
                nickname_index_sql = nickname_index_table.insert().values(nickname=nickname.lower(), user_id=user['user_id'])
                sqls.append(nickname_index_sql)
                models.exec_change(*sqls)


if __name__ == '__main__':
    table_names = models.get_table_names('user_info')
    for table_name in table_names:
        treat_nickname_index(table_name)
