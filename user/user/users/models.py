# -*- coding: utf-8 -*-


import hashlib

from sqlalchemy import create_engine, MetaData, event, DDL
from sqlalchemy import (Table, Column, BigInteger, Integer, String, Date, DateTime,
                        Boolean, SmallInteger, UniqueConstraint, Float)
from sqlalchemy.dialects.mysql import TINYINT

import constants


engine = create_engine(constants.DB_USER_URI + '?charset=utf8',
                       encoding='utf-8',
                       convert_unicode=True,
                       pool_recycle=constants.DB_POOL_RECYCLE,
                       pool_size=constants.DB_POOL_SIZE,
                       echo=constants.DB_ECHO)


meta = MetaData(bind=engine)

# 用户资料表
user_info_tables = {}
def get_user_info_table(user_id):
    shard_id = int(user_id) / constants.DB_USER_SHARD_NUM
    table = user_info_tables.get(shard_id)
    if table is None:
        table = Table('user_info_%d' % shard_id, meta,
                      Column('user_id', BigInteger, primary_key=True),
                      Column('username', String(20)),
                      # 0 禁用账号, 1 玩家, 2 主播
                      Column('user_type', TINYINT(1), nullable=False, default=1),
                      Column('nickname', String(20)),
                      Column('password', String(40)),
                      Column('email', String(30)),
                      Column('mobile', String(15)),
                      Column('email_verified', Boolean()),
                      Column('mobile_verified', Boolean()),
                      Column('cover', String(30)),
                      Column('avatar', String(30)),
                      Column('status_text', String(140)),
                      Column('gender', String(1)), # m表示男，f表示女，u表示未知
                      Column('qq', String(20)),
                      Column('birthday', Date),
                      Column('user_ip', BigInteger),
                      Column('channel', String(15)),  # 注册渠道
                      Column('platform', SmallInteger, nullable=False),
                      Column('create_time', BigInteger, nullable=False),
                      Column('update_time', BigInteger, nullable=False),
                      UniqueConstraint('nickname', name='unique_nickname'),
                      extend_existing=True,
                      mysql_charset='utf8',
                      mysql_engine='InnoDB')
        table.create(checkfirst=True)
        user_info_tables[shard_id] = table

    return table


# 邮箱索引表
email_index_tables = {}
def get_email_index_table(email):
    shard_id = int(hashlib.md5(email).hexdigest(), 16) % constants.DB_EMAIL_SHARD_MOD
    table = email_index_tables.get(shard_id)
    if table is None:
        table = Table('email_index_%d' % shard_id, meta,
                Column('email', String(30), primary_key=True),
                Column('user_id', BigInteger, nullable=False),
                extend_existing=True,
                mysql_charset='utf8',
                mysql_engine='InnoDB')
        table.create(checkfirst=True)
        email_index_tables[shard_id] = table

    return table


# 用户名索引表
username_index_tables = {}
def get_username_index_table(username):
    shard_id = int(hashlib.md5(username.encode('utf-8')).hexdigest(), 16) % constants.DB_USERNAME_SHARD_MOD
    table = username_index_tables.get(shard_id)
    if table is None:
        table = Table('username_index_%d' % shard_id, meta,
                Column('username', String(20), primary_key=True),
                Column('user_id', BigInteger, nullable=False),
                extend_existing=True,
                mysql_charset='utf8',
                mysql_engine='InnoDB')
        table.create(checkfirst=True)
        username_index_tables[shard_id] = table

    return table


# 昵称索引表
# 昵称中的字母统一按小写形式存储
nickname_index_tables = {}
def get_nickname_index_table(nickname):
    shard_id = int(hashlib.md5(nickname.encode('utf-8')).hexdigest(), 16) % constants.DB_USERNAME_SHARD_MOD
    table = nickname_index_tables.get(shard_id)
    if table is None:
        table = Table('nickname_index_%d' % shard_id, meta,
                Column('nickname', String(20), primary_key=True),
                Column('user_id', BigInteger, nullable=False),
                extend_existing=True,
                mysql_charset='utf8',
                mysql_engine='InnoDB')
        table.create(checkfirst=True)
        nickname_index_tables[shard_id] = table

    return table


# 手机号码索引表
mobile_index_tables = {}
def get_mobile_index_table(mobile):
    shard_id = int(hashlib.md5(mobile).hexdigest(), 16) % constants.DB_MOBILE_SHARD_MOD
    table = mobile_index_tables.get(shard_id)
    if table is None:
        table = Table('mobile_index_%d' % shard_id, meta,
                Column('mobile', String(15), primary_key=True),
                Column('user_id', BigInteger, nullable=False),
                extend_existing=True,
                mysql_charset='utf8',
                mysql_engine='InnoDB')
        table.create(checkfirst=True)
        mobile_index_tables[shard_id] = table

    return table


# device索引表
device_index_tables = {}
def get_device_index_table(device):
    shard_id = int(hashlib.md5(device).hexdigest(), 16) % constants.DB_DEVICE_SHARD_MOD
    table = device_index_tables.get(shard_id)
    if table is None:
        table = Table('device_index_%d' % shard_id, meta,
                Column('device_hash', String(32), primary_key=True),
                Column('user_id', BigInteger, nullable=False),
                Column('platform', SmallInteger, nullable=False),
                Column('device_info', String(30)),
                extend_existing=True,
                mysql_charset='utf8',
                mysql_engine='InnoDB')
        table.create(checkfirst=True)
        device_index_tables[shard_id] = table

    return table

# imei索引表
imei_index_tables = {}
def get_imei_index_table(imei):
    shard_id = int(hashlib.md5(imei).hexdigest(), 16) % constants.DB_DEVICE_SHARD_MOD
    table = imei_index_tables.get(shard_id)
    if table is None:
        table = Table('imei_index_%d' % shard_id, meta,
                      Column('imei', String(30), primary_key=True),
                      Column('device_hash', String(32)),
                      Column('user_id', BigInteger, nullable=False),
                      Column('platform', SmallInteger, nullable=False),
                      extend_existing=True,
                      mysql_charset='utf8',
                      mysql_engine='InnoDB')
        table.create(checkfirst=True)
        imei_index_tables[shard_id] = table

    return table


# 第三方用户登录
oauth2_table = Table('oauth2_user', meta,
                    Column('open_id', String(50), primary_key=True),
                    Column('user_id', BigInteger, nullable=False),
                    Column('channel', String(10), nullable=False),
                    extend_existing=True,
                    mysql_charset='utf8',
                    mysql_engine='InnoDB')

oauth2_table.create(checkfirst=True)


# 环信用户信息
im_tables = {}
def get_im_table(user_id):
    shard_id = int(user_id) / constants.DB_USER_SHARD_NUM
    table = im_tables.get(shard_id)
    if table is None:
        table = Table('im_user_%d' % shard_id, meta,
                      Column('user_id', BigInteger, primary_key=True),
                      Column('platform', SmallInteger, nullable=False),
                      Column('username', String(20), nullable=False),
                      Column('password', String(40), nullable=False),
                      extend_existing=True,
                      mysql_charset='utf8',
                      mysql_engine='InnoDB')
        table.create(checkfirst=True)
        im_tables[shard_id] = table

    return table

#主播表
master_user_table = Table('master_user', meta,
                      Column('user_id', BigInteger, primary_key=True),
                      Column('nickname', String(20)),
                      Column('room_id', Integer),    # 该主播创建的直播间ID
                      Column('is_recommended', TINYINT(1), nullable=False, default=0),
                      Column('sort', Integer, nullable=False, default=0),
                      Column('is_deleted', TINYINT(1), nullable=False, default=0),
                      extend_existing=True,
                      mysql_charset='utf8',
                      mysql_engine='InnoDB')

master_user_table.create(checkfirst=True)

def get_master_user_table():
    return master_user_table


# 关注表
user_follow_tables = {}
def get_user_follow_table(user_id):
    shard_id = int(user_id) / constants.DB_USER_RELATION_SHARD_NUM
    table = user_follow_tables.get(shard_id)
    if table is None:
        table = Table('user_follow_%d' % shard_id, meta,
                    Column('id', Integer, primary_key=True),
                    Column('user_id', BigInteger, nullable=False),
                    Column('follow_user_id', BigInteger, nullable=False),
                    Column('created', DateTime, nullable=False),
                    Column('parent_id', BigInteger, nullable=False, server_default="0"),
                    UniqueConstraint('user_id', 'follow_user_id', name='unique_2_user_id'),
                    mysql_engine='InnoDB')
        table.create(checkfirst=True)
        user_follow_tables[shard_id] = table
    return table


"""
粉丝表

id:                 id
user_id:            用户id
fans_user_id:       粉丝用户id
created:            创建时间
parent_id:          某用户关注主播时同时增加的虚拟粉丝此项填入真实用户的id, 当取消关注时一起取消关注
notification:       粉丝是否接受开播推送通知
"""
user_fans_tables = {}
def get_user_fans_table(user_id):
    shard_id = int(user_id) / constants.DB_USER_RELATION_SHARD_NUM
    table = user_fans_tables.get(shard_id)
    if table is None:
        table = Table('user_fans_%d' % shard_id, meta,
                    Column('id', Integer, primary_key=True),
                    Column('user_id', BigInteger, nullable=False),
                    Column('fans_user_id', BigInteger, nullable=False),
                    Column('created', DateTime, nullable=False),
                    Column('parent_id', BigInteger, nullable=False, server_default="0"),
                    Column('notification', TINYINT(1), nullable=False, default=1),
                    UniqueConstraint('user_id', 'fans_user_id', name='unique_2_user_id'),
                    mysql_engine='InnoDB')
        table.create(checkfirst=True)
        user_fans_tables[shard_id] = table
    return table


report_table = Table("report", meta,
                     Column("id",Integer,primary_key=True),
                     Column("reported_uid", Integer, nullable=False),
                     Column("user_id", Integer, nullable=False),
                     Column("created", DateTime, nullable=False),
                     Column("is_deleted", Boolean, nullable=False, default=False),
                     Column("report_type", Integer, nullable=False, default=0),
                     UniqueConstraint("reported_uid","user_id","report_type",name = "unique_1"),
                     mysql_engine = "InnoDB")

event.listen(
    report_table,
    "after_create",
    DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 10001;")
)

def get_report_table():
    return report_table


"""
银行卡认证信息表

参数:
user_id:                用户id
card_num:               银行卡号
bank_name:              开户行
card_holder:            持卡人姓名
"""
bankcard_cert_table = Table('bankcard_cert', meta,
                            Column('id', Integer, primary_key=True),
                            Column('user_id', BigInteger, nullable=False),
                            Column('card_num', String(50), nullable=False),
                            Column('bank_name', String(50), nullable=False),
                            Column('card_holder', String(50), nullable=False),
                            extend_existing=True,
                            mysql_charset='utf8',
                            mysql_engine='InnoDB')
bankcard_cert_table.create(checkfirst=True)
def get_bankcard_cert_table():
    return bankcard_cert_table


"""
主播合约表
一个主播可以拥有多条合约纪录
根据合约的生效月份倒序排序后最新的且不超过当前月份的为当前生效合约

参数:
user_id:                主播的id
contract_type:          主播的签约类型, 0为未签约, 1为签约
rank_reward_bonus_rate  主播的排名奖金倍数, 默认情况下未签约的为0.5x, 签约不拿底薪的为1x, 签约拿底薪的为0x
basic_salary:           主播的底薪, 只针对签约底薪的主播, 其他主播为0
gift_exponent_share:    主播的收礼指数提成百分比, 默认为50%
start_from:             合约的生效开始月份, 统一为当月1号00:00:00
"""
contract_table = Table('contract', meta,
                       Column('id', Integer, primary_key=True),
                       Column('user_id', BigInteger, nullable=False),
                       Column('contract_type', TINYINT(1), nullable=False, default=0),
                       Column('rank_reward_bonus_rate', Float, nullable=False),
                       Column('basic_salary', Integer, nullable=False, default=0),
                       Column('gift_exponent_share', Float, nullable=False, default=0.5),
                       Column('start_from', DateTime, nullable=False),
                       extend_existing=True,
                       mysql_charset='utf8',
                       mysql_engine='InnoDB')
contract_table.create(checkfirst=True)
def get_contract_table():
    return contract_table


def get_table_names(main_name):
    '''
    获取某个表的所有分表名
    参数：
        main_name  表名的主体部分，如 user_views_0 的主体部分为 user_views
    '''
    conn = engine.connect()
    sql = 'SHOW TABLES LIKE "%s_%%%%"' % main_name
    ret = conn.execute(sql).fetchall()
    table_names = []
    for item in ret:
        table_names.append(item[0])
    return table_names


def exec_query(sql, islist=False):
    conn = engine.connect()
    try:
        ret = []
        for one in conn.execute(sql).fetchall():
            ret.append(dict(one.items()))
        if not islist:
            return ret if len(ret) != 1 else ret[0]
        return ret
    except:
        raise
    finally:
        conn.close()

def exec_change(*args):
    conn = engine.connect()
    trans = conn.begin()
    try:
        ret = []
        for sql in args:
            ret.append(conn.execute(sql))
        trans.commit()
        return ret if len(ret) != 1 else ret[0]
    except:
        trans.rollback()
        raise
    finally:
        conn.close()

def drop_all():
    meta.reflect(engine)
    meta.drop_all()

def create_all():
    meta.reflect(engine)
    meta.create_all()
