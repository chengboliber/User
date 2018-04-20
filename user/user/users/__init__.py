# -*- coding: utf-8 -*-

from datetime import datetime

from . import models

BANK_CERT_INFO_TABLE = models.get_bankcard_cert_table()
CONTRACT_TABLE = models.get_contract_table()

def get_oauth2_info(**data):
    table = models.oauth2_table
    sql = table.select()\
        .where(table.c.open_id == data['open_id'])\
        .where(table.c.channel == data['channel'])
    row = models.exec_query(sql)
    return row if row else {}


def get_im_info(user_id):
    table = models.get_im_table(user_id)
    sql = table.select().where(table.c.user_id == user_id)
    row = models.exec_query(sql)
    return row if row else {}


def get_user_info(user_id):
    table = models.get_user_info_table(user_id)
    select_sql = table.select().where(table.c.user_id == user_id)
    row = models.exec_query(select_sql)
    return row if row else {}


def get_user_by_device(device_hash):
    table = models.get_device_index_table(device_hash)
    select_sql = table.select().where(table.c.device_hash == device_hash)
    row = models.exec_query(select_sql)
    return row if row else {}


def get_user_by_imei(imei):
    table = models.get_imei_index_table(imei)
    select_sql = table.select().where(table.c.imei == imei)
    row = models.exec_query(select_sql)
    return row if row else {}


def get_user_by_username(username):
    table = models.get_username_index_table(username)
    select_sql = table.select().where(table.c.username == username)
    row = models.exec_query(select_sql)
    return row if row else {}


def get_user_by_email(email):
    table = models.get_email_index_table(email)
    select_sql = table.select().where(table.c.email == email)
    row = models.exec_query(select_sql)
    return row if row else {}


def get_user_by_mobile(mobile):
    table = models.get_mobile_index_table(mobile)
    select_sql = table.select().where(table.c.mobile == mobile)
    row = models.exec_query(select_sql)
    return row if row else {}


def is_nickname_exists(nickname):
    ''' 判断昵称是否存在 '''
    user_id = get_user_id_by_nickname(nickname)
    return True if user_id else False

def get_user_id_by_nickname(nickname):
    ''' 通过昵称查找 user_id '''
    if not isinstance(nickname, unicode):
        nickname = nickname.decode('utf8')
    nickname = nickname.lower()
    table = models.get_nickname_index_table(nickname)
    sql = table.select(table.c.nickname == nickname)
    row = models.exec_query(sql)
    return row['user_id'] if row else None


def get_master(**data):
    ''' 推荐主播排在前面 '''
    table = models.get_master_user_table()
    sql = table.select(table.c.is_deleted == 0)\
        .order_by(table.c.is_recommended.desc())\
        .order_by(table.c.sort.desc())\
        .order_by(table.c.user_id.desc())\
        .offset(data['offset']).limit(data['limit'])
    return models.exec_query(sql, islist=True)


def forbid_user(user_id, user_type=0):
    ''' 禁用/解禁账号 '''
    if user_type not in [0, 1]:
        return False
    table = models.get_user_info_table(user_id)
    sql = table.update(table.c.user_id == user_id).values(user_type=user_type)
    return models.exec_change(*[sql])


def unforbid_user(user_id):
    ''' 解禁账号 '''
    return forbid_user(user_id, 1)


def follow_user(**data):
    ''' 关注用户 '''
    fans_user_id = data['user_id']
    follow_user_id = data['follow_user_id']
    parent_id = data.get('parent_id',0)
    now = datetime.now()
    data['created'] = now

    sqls = []
    follow_table = models.get_user_follow_table(fans_user_id)
    follow_sql = follow_table.insert({
                'user_id': fans_user_id,
                'follow_user_id': follow_user_id,
                'created': now,
                'parent_id': parent_id
                })
    sqls.append(follow_sql)
    fans_table = models.get_user_fans_table(follow_user_id)
    fans_sql = fans_table.insert({
                'user_id': follow_user_id,
                'fans_user_id': fans_user_id,
                'created': now,
                'parent_id': parent_id
                })
    sqls.append(fans_sql)

    return models.exec_change(*sqls)


def unfollow_user(**data):
    ''' 取消关注 '''
    fans_user_id = data['user_id']
    follow_user_id = data['follow_user_id']

    sqls = []
    table = models.get_user_follow_table(fans_user_id)
    sql = table.delete()\
                .where(table.c.user_id == fans_user_id)\
                .where(table.c.follow_user_id == follow_user_id)
    sqls.append(sql)
    table = models.get_user_fans_table(follow_user_id)
    sql = table.delete()\
                .where(table.c.user_id == follow_user_id)\
                .where(table.c.fans_user_id == fans_user_id)
    sqls.append(sql)

    return models.exec_change(*sqls)


def is_follow(user_id, follow_user_id):
    ''' 是否关注 '''
    table = models.get_user_follow_table(user_id)
    sql = table.select(table.c.user_id == user_id)\
                .where(table.c.follow_user_id == follow_user_id)
    ret = models.exec_query(sql)
    return True if ret else False


def get_user_follow(user_id, offset=0, limit=-1):
    ''' 获取用户的关注列表 '''
    table = models.get_user_follow_table(user_id)
    sql = table.select(table.c.user_id == user_id)\
                .order_by(table.c.created.desc())\
                .order_by(table.c.id.desc())\
                .offset(offset)
    if limit > 0:
        sql = sql.limit(limit)

    return models.exec_query(sql, islist=True)


def get_user_fans(user_id, offset=0, limit=-1):
    ''' 获取用户的粉丝列表 '''
    table = models.get_user_fans_table(user_id)
    sql = table.select(table.c.user_id == user_id)\
                .order_by(table.c.created.desc())\
                .order_by(table.c.id.desc())\
                .offset(offset)
    if limit > 0:
        sql = sql.limit(limit)

    return models.exec_query(sql, islist=True)


def get_user_real_fans(user_id):
    ''' 获取用户真实fans '''
    table = models.get_user_fans_table(user_id)
    sql = table.select(table.c.user_id == user_id)\
               .where(table.c.parent_id == 0)
    return models.exec_query(sql, islist=True)


def get_vfans_users(user_id, real_fans_users = None, limit=0):
    ''' 获取虚拟粉丝用户 '''
    table = models.get_user_info_table(user_id)
    sql = table.select(table.c.mobile == None)
    if real_fans_users:
        real_fans_user_ids = [i["fans_user_id"] for i in real_fans_users]
        real_fans_user_ids.append(user_id)
        sql = sql.where(table.c.user_id.notin_(real_fans_user_ids))\
                 .where(table.c.nickname!=None)\
                 .where(table.c.nickname!="")
    if limit > 0:
        sql = sql.limit(limit)
    return models.exec_query(sql, islist=True)


def get_vfans_users_by_parent_id(follow_user_id, parent_id):
    ''' 获取关注时获取随机关在的虚拟粉丝 '''
    table = models.get_user_fans_table(follow_user_id)
    sql = table.select(table.c.user_id == follow_user_id)\
               .where(table.c.parent_id == parent_id)
    return models.exec_query(sql, islist=True)


def get_user_recent_fans(user_id, start_time, end_time):
    ''' 获取用户近几日的粉丝列表 '''
    table = models.get_user_fans_table(user_id)
    sql = table.select(table.c.user_id == user_id)\
                .where(table.c.created > start_time)\
                .where(table.c.created < end_time)

    return models.exec_query(sql, islist=True)

def get_report_user_by_user_id(reported_uid,user_id,report_type=0):
    table = models.get_report_table()
    sql = table.select(table.c.reported_uid==reported_uid) \
               .where(table.c.user_id==user_id) \
               .where(table.c.report_type==report_type)
    return models.exec_query(sql, islist=False)

def create_report_user(reported_uid,user_id,report_type=0):
    report_info = get_report_user_by_user_id(
                      reported_uid,user_id,report_type)
    if report_info:
        return -1
    now = datetime.now()
    table = models.get_report_table()
    sql = table.insert().values(reported_uid=reported_uid,user_id=user_id,
                                report_type=report_type,created=now)
    rs = models.exec_change(sql)
    return rs.inserted_primary_key[0]


def search_master_users(nickname):
    ''' 搜索主播用户 '''
    table = models.get_master_user_table()
    sql = table.select(table.c.is_deleted==0)\
            .where(table.c.room_id > 0)\
            .where(table.c.nickname.like('%%%s%%' % nickname))\
            .limit(1000)
    return models.exec_query(sql, islist=True)


def update_master_user(user_id, **kwargs):
    ''' 更新主播表 '''
    table = models.get_master_user_table()
    sql = table.update(table.c.user_id==user_id)\
                .values(**kwargs)
    return models.exec_change(sql)


def insert_bank_info(**data):
    """
    为某个用户插入新的银行卡认证纪录
    """
    user_id = data.pop('user_id')
    table = BANK_CERT_INFO_TABLE
    if get_bank_info(user_id) != {}:
        sql = table.update(table.c.user_id == user_id)\
            .values(**data)
    else:
        sql = table.insert({
            'user_id': user_id,
            'card_num': data['card_num'],
            'bank_name': data['bank_name'],
            'card_holder': data['card_holder']
        })
    return models.exec_change(sql)


def get_bank_info(user_id):
    """
    查询某个用户的银行卡认证纪录
    """
    table = BANK_CERT_INFO_TABLE
    sql = table.select().where(table.c.user_id == user_id)
    row = models.exec_query(sql)
    return row if row else {}


def insert_contract(**data):
    """
    为某个用户插入新的合约纪录
    """
    sql = CONTRACT_TABLE.insert({
        'user_id': data['user_id'],
        'contract_type': data['contract_type'],
        'rank_reward_bonus_rate': data['rank_reward_bonus_rate'],
        'basic_salary': data['basic_salary'],
        'gift_exponent_share': data['gift_exponent_share'],
        'start_from': data['start_from']
    })
    return models.exec_change(sql)


def get_all_contract(user_id):
    """
    查询某个用户的所有合约纪录
    """
    table = CONTRACT_TABLE
    sql = table.select().where(table.c.user_id == user_id)
    rows = models.exec_query(sql)
    return rows if rows else {}


def get_current_contract(user_id):
    """
    查询某个用户的当前激活合约
    如果用户当前没有合约则为用户插入状态为未签约的合约
    """
    table = CONTRACT_TABLE
    now = datetime.now()
    today = '%s-%s-%s 00:00:00' % (now.year, now.month, now.day)
    sql = table.select()\
        .where(table.c.user_id == user_id)\
        .where(table.c.start_from <= today)\
        .order_by(table.c.start_from.desc())\
        .limit(1)
    row = models.exec_query(sql)
    if not row:
        contract_data = {
            'user_id': user_id,
            'contract_type': 0,
            'rank_reward_bonus_rate': 0.5,
            'basic_salary': 0,
            'gift_exponent_share': 0.7,
            'start_from': '%s-%s-01 00:00:00' % (now.year, now.month)
        }
        insert_contract(**contract_data)
        row = models.exec_query(sql)
    return row if row else {}


def get_next_contract(user_id, now):
    """
    查询某个用户的下一个生效合约
    """
    table = CONTRACT_TABLE
    sql = table.select()\
        .where(table.c.user_id == user_id)\
        .where(table.c.start_from > now)\
        .order_by(table.c.start_from.desc())\
        .limit(1)
    row = models.exec_query(sql)
    return row if row else {}


def notification_modify(user_id, master_user_id, modify=1):
    """
    某用户打开接收某主播的开播通知
    :param user_id:                         用户id
    :param master_user_id:                  主播id
    :param modify:                          状态如何改变, 1为改为开启, 0为改为关闭
    """
    table = models.get_user_fans_table(master_user_id)
    sql = table.update()\
        .where(table.c.user_id == master_user_id)\
        .where(table.c.fans_user_id == user_id)\
        .values(notification=modify)
    return models.exec_change(sql)


def notification_check(user_id, master_user_id):
    """
    检查某用户当前是否接收某主播的开播通知
    :param user_id:                         用户id
    :param master_user_id:                  主播id
    """
    table = models.get_user_fans_table(master_user_id)
    sql = table.select()\
        .where(table.c.user_id == master_user_id)\
        .where(table.c.fans_user_id == user_id)
    row = models.exec_query(sql)
    return row if row else False


def master_set(user_id):
    """
    将某个用户设置为主播
    :param user_id:                         用户id
    """
    user_info_table = models.get_user_info_table(user_id)
    sql = user_info_table.update()\
        .where(user_info_table.c.user_id == user_id)\
        .values(user_type=2)
    models.exec_change(sql)

    user_info = get_user_info(user_id)

    master_user_table = models.get_master_user_table()
    sql = master_user_table.select()\
        .where(master_user_table.c.user_id == user_id)
    row = models.exec_query(sql)
    if row:
        sql = master_user_table.update()\
            .where(master_user_table.c.user_id == user_id)\
            .values(is_deleted=0)
    else:
        sql = master_user_table.insert({
            'user_id': user_id,
            'nickname': user_info['nickname'],
            'is_recommended': 0,
            'sort': 0,
            'is_deleted': 0
        })
    return models.exec_change(sql)


def master_unset(user_id):
    """
    将某个用户主播资格撤销
    :param user_id:                             用户id
    """
    user_info_table = models.get_user_info_table(user_id)
    sql = user_info_table.update()\
        .where(user_info_table.c.user_id == user_id)\
        .values(user_type=1)
    models.exec_change(sql)

    master_user_table = models.get_master_user_table()
    sql = master_user_table.update()\
        .where(master_user_table.c.user_id == user_id)\
        .values(is_deleted=1)
    return models.exec_change(sql)
