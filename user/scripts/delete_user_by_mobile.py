# _*_ coding: utf_8 _*_

import os
import sys

_basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

from user.users import models


def delete(mobile):
    user_table = models.get_user_info_table(10001)
    sql = user_table.select().where(user_table.c.mobile == mobile)
    user_info = models.exec_query(sql)
    print user_info

    sqls = []
    new_mobile = 'm_{mobile}'.format(mobile=mobile)
    user_sql = user_table.update(user_table.c.mobile == mobile).values(mobile=new_mobile)
    sqls.append(user_sql)

    mobile_table = models.get_mobile_index_table(mobile)
    print mobile_table
    mobile_sql = mobile_table.delete().where(mobile_table.c.mobile == mobile)
    sqls.append(mobile_sql)

    new_mobile_table = models.get_mobile_index_table(new_mobile)
    print new_mobile_table
    mobile_insert_sql = new_mobile_table.insert()\
        .values(mobile=new_mobile, user_id=user_info['user_id'])
    sqls.append(mobile_insert_sql)

    models.exec_change(*sqls)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'input mobile'
        sys.exit(1)
    delete(sys.argv[1])
