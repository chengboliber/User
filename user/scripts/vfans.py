#-*- coding:utf-8 -*-
import redis
import pymysql
import random
import time
from operator import itemgetter
from datetime import datetime, date

MYSQL_CONNETION_SETTINGS = dict(
    host = "192.168.0.88",
    port = 43306,
    user = "zwc",
    passwd = "123",
    db = "tl_user",
    autocommit = False,
)

rc = redis.Redis(
    host = "192.168.0.88",
    port = 46379,
    db = 0
)

REDIS_USER_COUNT = 'tl:user:count:{user_id}'
USER_FOLLOW_COUNT = 'follow_count'
USER_FANS_COUNT = 'fans_count'

def redis_incr_fans_count(user_id, fans_user_ids):
    if not isinstance(fans_user_ids, (list, tuple)):
        return
    rpipe = rc.pipeline()
    fans_key = REDIS_USER_COUNT.format(user_id = user_id)
    """ 主播粉丝数增加 """
    rpipe.hincrby(fans_key, USER_FANS_COUNT, len(fans_user_ids))
    for fans_user_id in fans_user_ids:
        follow_key = REDIS_USER_COUNT.format(user_id = fans_user_id)
        """ 粉丝的关注数加一 """
        rpipe.hincrby(follow_key, USER_FOLLOW_COUNT, 1)
    rpipe.execute()

def generate_datetimes(count):
    """
    根据当前时间随机生成关注时间
    """
    now_dt = datetime.now()
    now = time.mktime(now_dt.timetuple())
    today = time.mktime(date.today().timetuple())
    start = today + 6 * 60 * 60
    if now_dt.hour > 12:
        start += 7 * 60 * 60
    end = now
    dts = [datetime.fromtimestamp(random.randrange(start, end)).strftime("%Y-%m-%d %H:%M:%S") \
           for i in range(count)]
    return dts

def create_connection():
    """
    创建mysql连接
    """
    return pymysql.connect(**MYSQL_CONNETION_SETTINGS)

def get_first_vfans_by_user_id(user_id):
    """
    根据用户ID获取首次关联用户信息，主要用于判断虚拟粉丝运行时间
    """
    _sql = "SELECT * FROM user_fans_{table_index} WHERE user_id={user_id} AND parent_id=-1 ORDER BY created ASC LIMIT 1" \
           .format(table_index = int(user_id / 100000), user_id = user_id)
    conn = create_connection()
    curs = conn.cursor(cursor = pymysql.cursors.DictCursor)
    curs.execute(_sql)
    result = curs.fetchone()
    curs.close()
    conn.close()
    return result

def get_fans_by_user_id(user_id, parent_id=None):
    """
    根据用户ID和parent_id来获取粉丝数
    """
    _sql = "SELECT fans_user_id FROM user_fans_{table_index} WHERE user_id={user_id}" \
           .format(table_index = int(user_id / 100000), user_id = user_id)
    if parent_id is not None:
        _sql += " AND parent_id={parent_id}".format(parent_id = parent_id)
    conn = create_connection()
    curs = conn.cursor()
    try:
        curs.execute(_sql)
        result = [i[0] for i in curs]
    except Exception,ex:
        print ex
        result = []
    curs.close()
    conn.close()
    return result

def get_vfans_by_user_id(user_id, limit=1):
    """
    根据用户ID获取需要新增的粉丝数
    """
    user_ids = get_fans_by_user_id(user_id)
    user_ids = user_ids or []
    user_ids.append(user_id)
    _sql = "SELECT user_id FROM user_info_{table_index} WHERE mobile IS NULL {notin_user_ids} AND nickname IS NOT NULL AND nickname != '' LIMIT {limit}" \
           .format(table_index = int(user_id / 1000000), 
                   notin_user_ids = " AND user_id NOT IN ({user_ids})" \
                                    .format(user_ids = ",".join(map(str, user_ids))) \
                                    if user_ids else "", 
                   limit = limit)
    conn = create_connection()
    curs = conn.cursor()
    try:
        curs.execute(_sql)
        result = [i[0] for i in curs]
    except Exception,ex:
        print ex
        result = []
    curs.close()
    conn.close()
    return result

def generate_vfans(user_id, fans_count):
    """
    给用户生成粉丝
    """
    if not fans_count: return 0
    vfans_ids = get_vfans_by_user_id(user_id, fans_count)
    print vfans_ids
    if not vfans_ids: return
    vfans_count = len(vfans_ids)
    dts = generate_datetimes(vfans_count)
    vfans_tuples = sorted(zip(vfans_ids, dts), key=itemgetter(1))
    fans_params = ",".join([str((user_id, vfans_id, dt, -1)) for vfans_id, dt in vfans_tuples])
    _fans_sql = "INSERT INTO user_fans_{table_index} (user_id, fans_user_id, created, parent_id) VALUES {fans_params}" \
                .format(table_index = int(user_id / 100000), fans_params = fans_params)
    follow_params = ",".join([str((vfans_id, user_id, dt, -1)) for vfans_id, dt in vfans_tuples])
    _follow_sql = "INSERT INTO user_follow_{table_index} (user_id, follow_user_id, created, parent_id) VALUES {follow_params}" \
                  .format(table_index = int(user_id / 100000), follow_params = follow_params)
    conn = create_connection()
    curs = conn.cursor()
    try:
        for sql in [_fans_sql, _follow_sql]:
            curs.execute(sql)
        conn.commit()
        redis_incr_fans_count(user_id, vfans_ids)
    except Exception,ex:
        print ex
        conn.rollback()
    curs.close()
    conn.close()

def get_zhubos():
    _sql = "SELECT user_id FROM {table_name} WHERE user_type=2"
    conn = create_connection()
    curs = conn.cursor()
    try:
        curs.execute("SHOW TABLES LIKE 'user_info_%'")
        table_names = [i[0] for i in curs]
        result = []
        for table_name in table_names:
            sql = _sql.format(table_name = table_name)
            curs.execute(sql)
            result.extend([i[0] for i in curs])
    except Exception,ex:
        print ex
        result = []
    curs.close()
    conn.close()
    return result

def main():
    zhubo_user_ids = get_zhubos()
    for user_id in zhubo_user_ids:
        vfans_user_info = get_first_vfans_by_user_id(user_id)
        # 判断虚拟粉是否持续新增了60天，持续60天则不需要增加了
        if vfans_user_info and \
           (datetime.now() - vfans_user_info["created"]).days > 60:
            continue
        fans_user_ids = get_fans_by_user_id(user_id, 0)
        # 判断真实用户数是否达到2000，达到2000则不需要增加了
        if len(fans_user_ids) >= 2000:
            continue
        vfans_count = random.randrange(0, 4)
        print "zhubo_user_id: %s, vfans_count: %s" % (user_id, vfans_count)
        generate_vfans(user_id, vfans_count)


# 每天定时两次，分别在12:00和20:00，每次随机区间为0~3，
# 相当于每天随机区间为0~6
if __name__ == "__main__":
    print 'TIME: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    main()







