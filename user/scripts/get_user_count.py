# _*_ coding: utf_8 _*_

import os
import sys
import time
from datetime import datetime, timedelta

_basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

from user.users import models


def user_count(day):
    user_table = models.get_user_info_table(10001)
    start_date = datetime.strptime(day, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    start_stamp = time.mktime(start_date.timetuple())
    end_stamp = time.mktime(end_date.timetuple())
    sql = user_table.select(user_table.c.user_id)\
        .where(user_table.c.create_time > int(start_stamp))\
        .where(user_table.c.create_time <= int(end_stamp))
    rs = models.exec_query(sql)
    print day, len(rs)


if __name__ == '__main__':
    if len(sys.argv[1]) == 1:
        day = '2015-02-02'
    else:
        day = sys.argv[1]
    user_count(day)
