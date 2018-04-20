# -*- coding: utf-8 -*-
'''
给App 主播用户发送系统消息
'''
import os
import sys

_basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

from user.users import models
from tlclient.messages.message import MessageClient

message_client = MessageClient()

def get_master_user_ids(user_id, limit=5000):
    sql = '''SELECT user_id FROM master_user
        WHERE user_id > {user_id}
        AND is_deleted = 0
        ORDER BY user_id ASC
        LIMIT {page_limit}'''.format(user_id=user_id, page_limit=limit)
    ret = models.exec_query(sql, islist=True)
    return [item['user_id'] for item in ret]


if __name__ == '__main__':

    # 消息内容，换行使用 \n
    msg_content =\
    u'亲爱的主播:\n结束直播后，请通过按结束直播按钮来停止直播，不要用杀后台进程的方式。若因为没有按结束按钮而导致直播间长时间黑屏，可能扣除直播凸币奖励。'

    last_user_id = 0
    while True:
        user_ids = get_master_user_ids(last_user_id)
        if not user_ids:
            break
        for user_id in user_ids:
            message_client.send_message(user_id=user_id, from_user_id=10001, type=9, ref_id=0, content=msg_content)
        last_user_id = user_ids[-1]
        print '[5000:%s] Done' % last_user_id
    print u'主播用户发送完毕.'

