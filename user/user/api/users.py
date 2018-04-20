# -*- coding: utf-8 -*-

import logging
import re
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from tlutil import errors, json
from tlutil.helpers import encrypt_password, validate_password
from tlutil.helpers import convert_dict, ip2int, filter_fields
from tlclient.zhibo.room import RoomClient

from .. import users as users_service
from ..filters import make_user_info, gen_vfans_count
from ..users import caches as user_caches
from ..users import forms as user_forms
from ..users import models as user_models
from ..users import constants as USER

bp = Blueprint('bp_user', __name__, url_prefix='/user')
room_client = RoomClient()


@bp.route('/user_id/', methods=['POST'])
def user_id():
    ''' 获取用户 ID '''
    data = user_forms.user_id_query_schema(convert_dict(request.json))
    nickname = data.get('nickname')

    user_id = None
    if nickname:
        user_id = users_service.get_user_id_by_nickname(nickname)

    return jsonify(user_id=user_id)


@bp.route('/device/register/', methods=['POST'])
def device_hash_register():
    data = user_forms.device_register_schema(convert_dict(request.json))
    user_info = users_service.get_user_by_device(data['device_hash'])
    if user_info:
        if 'imei' in data:
            imei_info = users_service.get_user_by_imei(data['imei'])
            if not imei_info:
                imei_data = {}
                imei_data['imei'] = data['imei']
                imei_data['user_id'] = user_info['user_id']
                imei_data['device_hash'] = data['device_hash']
                imei_data['platform'] = data['platform']
                imei_table = user_models.get_imei_index_table(data['imei'])
                imei_insert_sql = imei_table.insert(imei_data)
                user_models.exec_change(imei_insert_sql)
        return jsonify({'user_id': user_info['user_id'], 'new': False})
    user_id = user_caches.incr_user_id()
    data['user_id'] = user_id
    data['user_ip'] = ip2int(data['user_ip'])

    user_fields = ['user_id', 'cover', 'avatar', 'user_ip', 'platform', 'gender']
    device_fields = ['user_id', 'device_hash', 'platform', 'device_info']
    user_data = filter_fields(data, user_fields)
    user_data['create_time'] = user_data['update_time'] = int(time.time())
    device_data = filter_fields(data, device_fields)

    sqls = []
    if 'imei' in data:
        imei_fields = ['user_id', 'imei', 'device_hash', 'platform']
        imei_data = filter_fields(data, imei_fields)
        imei_table = user_models.get_imei_index_table(data['imei'])
        imei_insert_sql = imei_table.insert(imei_data)
        sqls.append(imei_insert_sql)
    user_table = user_models.get_user_info_table(data['user_id'])
    user_insert_sql = user_table.insert(user_data)
    sqls.append(user_insert_sql)
    device_table = user_models.get_device_index_table(data['device_hash'])
    device_insert_sql = device_table.insert(device_data)
    sqls.append(device_insert_sql)
    user_models.exec_change(*sqls)

    return jsonify({'user_id': user_id, 'new': True})


@bp.route('/mobile/register/', methods=['POST'])
def mobile_register():
    data = user_forms.mobile_register_schema(convert_dict(request.json))
    mobile = data['mobile']
    nickname = data['nickname']
    user_info = users_service.get_user_by_mobile(mobile)
    if user_info:
        raise errors.ErrMobileExist
    user_id = user_caches.incr_user_id()
    data['user_id'] = user_id
    data['user_ip'] = ip2int(data['user_ip'])
    data['password'] = encrypt_password(data['password'])

    # 判断昵称是否已经存在
    if users_service.is_nickname_exists(nickname):
        data['nickname'] = '%s%s' % (data['nickname'][:12], user_id)
        nickname = data['nickname']

    user_fields = ['user_id', 'nickname', 'mobile', 'password', 'cover',
                   'avatar', 'user_ip', 'gender', 'platform', 'channel']
    user_data = filter_fields(data, user_fields)
    user_data['mobile_verified'] = True
    user_data['create_time'] = user_data['update_time'] = int(time.time())

    user_table = user_models.get_user_info_table(user_id)
    user_insert_sql = user_table.insert().values(**user_data)
    mobile_table = user_models.get_mobile_index_table(mobile)
    mobile_insert_sql = mobile_table.insert()\
        .values(mobile=mobile, user_id=user_id)
    nickname_index_table = user_models.get_nickname_index_table(nickname.lower())
    nickname_index_sql = nickname_index_table.insert().values(nickname=nickname.lower(), user_id=user_id)
    user_models.exec_change(user_insert_sql, mobile_insert_sql, nickname_index_sql)

    return jsonify({'user_id': user_id})


@bp.route('/email/register/', methods=['POST'])
def email_register():
    data = user_forms.email_register_schema(convert_dict(request.json))
    email = data['email']
    user_info = users_service.get_user_by_email(email)
    if user_info:
        raise errors.ErrEmailExist
    user_id = user_caches.incr_user_id()
    data['user_id'] = user_id
    data['user_ip'] = ip2int(data['user_ip'])
    data['password'] = encrypt_password(data['password'])

    user_fields = ['user_id', 'email', 'password',
                   'cover', 'avatar', 'user_ip', 'platform', 'gender']
    user_data = filter_fields(data, user_fields)
    user_data['create_time'] = user_data['update_time'] = int(time.time())

    user_table = user_models.get_user_info_table(user_id)
    user_insert_sql = user_table.insert().values(**user_data)
    email_table = user_models.get_email_index_table(email)
    email_insert_sql = email_table.insert()\
        .values(email=email, user_id=user_id)
    user_models.exec_change(user_insert_sql, email_insert_sql)

    return jsonify({'user_id': user_id})

@bp.route('/query/', methods=['POST'])
def query():
    data = user_forms.user_query_schema(convert_dict(request.json))
    value = data['value']
    type = data['type']
    if type == 'username':
        if re.match(u'^\u73a9\u5bb6', value):
            user_id = int(value[2:])
            return jsonify({'user_id': user_id})
        else:
            user_info = users_service.get_user_by_username(value)
    elif type == 'email':
        user_info = users_service.get_user_by_email(value)
    elif type == 'mobile':
        user_info = users_service.get_user_by_mobile(value)
    elif type == 'device_hash':
        user_info = users_service.get_user_by_device_hash(value)
    elif type == 'imei':
        user_info = users_service.get_user_by_imei(value)
    if not user_info:
        raise errors.ErrUserNotExist
    return jsonify({'user_id': user_info['user_id']})


@bp.route('/profile/', methods=['GET'])
def profile():
    data = user_forms.user_id_schema(convert_dict(request.args))
    user_info = users_service.get_user_info(data['user_id'])
    if not user_info:
        raise errors.ErrUserNotExist
    return jsonify(make_user_info(user_info))


@bp.route('/profile/bulk/', methods=['GET'])
def profile_bulk():
    data = user_forms.user_ids_schema(convert_dict(request.args))
    user_profiles = dict()
    for user_id in data['user_ids']:
        user_info = users_service.get_user_info(user_id)
        if not user_info:
            continue
        user_profiles[user_id] = make_user_info(user_info)

    return jsonify(user_profiles)


@bp.route('/cover/change/', methods=['POST'])
def change_cover():
    data = user_forms.cover_change_schema(convert_dict(request.json))
    user_id = data['user_id']
    user_info = users_service.get_user_info(user_id)
    if not user_info:
        raise errors.ErrUserNotExist

    user_table = user_models.get_user_info_table(user_id)
    update_sql = user_table.update()\
            .where(user_table.c.user_id == user_id)\
            .values(cover=data['new_cover'], update_time=int(time.time()))
    user_models.exec_change(update_sql)

    return jsonify()

@bp.route('/avatar/change/', methods=['POST'])
def change_avatar():
    data = user_forms.avatar_change_schema(convert_dict(request.json))
    user_id = data['user_id']
    user_info = users_service.get_user_info(user_id)
    if not user_info:
        raise errors.ErrUserNotExist

    user_table = user_models.get_user_info_table(user_id)
    update_sql = user_table.update()\
            .where(user_table.c.user_id == user_id)\
            .values(avatar=data['new_avatar'], update_time=int(time.time()))
    user_models.exec_change(update_sql)

    return jsonify()

@bp.route('/password/change/', methods=['POST'])
def change_password():
    data = user_forms.password_change_schema(convert_dict(request.json))
    user_id = data['user_id']
    user_info = users_service.get_user_info(user_id)
    if not user_info:
        raise errors.ErrUserNotExist
    if not validate_password(user_info['password'], data['old_password']):
        raise errors.ErrPasswordWrong

    user_table = user_models.get_user_info_table(user_id)
    update_sql = user_table.update()\
            .where(user_table.c.user_id == user_id)\
            .values(password=encrypt_password(data['new_password']), update_time=int(time.time()))
    user_models.exec_change(update_sql)

    return jsonify()

@bp.route('/password/reset/', methods=['POST'])
def reset_password():
    data = user_forms.password_reset_schema(convert_dict(request.json))
    user_id = data['user_id']
    user_info = users_service.get_user_info(user_id)
    if not user_info:
        raise errors.ErrUserNotExist

    user_table = user_models.get_user_info_table(user_id)
    update_sql = user_table.update()\
            .where(user_table.c.user_id == user_id)\
            .values(password=encrypt_password(data['new_password']), update_time=int(time.time()))
    user_models.exec_change(update_sql)

    return jsonify()

@bp.route('/auth/', methods=['POST'])
def auth():
    data = user_forms.user_auth_schema(convert_dict(request.json))
    user_id = data.get('user_id')
    email = data.get('email')
    mobile = data.get('mobile')
    username = data.get('username')
    if 'password' not in data and len(data.keys()) != 2:
        raise errors.ErrArgs
    if username:
        user = users_service.get_user_by_username(username)
    if email:
        user = users_service.get_user_by_email(email)
    if mobile:
        user = users_service.get_user_by_mobile(mobile)
    if not user_id and not user:
        raise errors.ErrUserNotExist
    user_id = user_id if user_id else user['user_id']

    user_info = users_service.get_user_info(user_id)
    if not user_info:
        raise errors.ErrUserNotExist
    if not user_info['password']:
        raise errors.ErrPasswordNotSet
    if not validate_password(user_info['password'], data['password']):
        raise errors.ErrPasswordWrong
    if user_info['user_type'] == 0:
        raise errors.ErrUserForbidden

    return jsonify(make_user_info(user_info))


@bp.route('/oauth2/register/', methods=['POST'])
def oauth2_register():
    data = user_forms.oauth2_register_schema(convert_dict(request.json))
    oauth2_info = users_service.get_oauth2_info(**data)
    if oauth2_info:
        raise errors.ErrOauthRegistered
    user_id = user_caches.incr_user_id()
    user_ip = data['user_ip']
    data['user_id'] = user_id
    data['user_ip'] = ip2int(user_ip)

    user_fields = ['user_id', 'nickname', 'cover',
                   'avatar', 'user_ip', 'platform', 'gender']
    user_data = filter_fields(data, user_fields)
    user_data['channel'] = data['from']
    user_data['create_time'] = user_data['update_time'] = int(time.time())
    oauth2_fields = ['open_id', 'user_id', 'channel']
    oauth2_data = filter_fields(data, oauth2_fields)

    # 如果用户昵称存在，则将昵称最后添加用户ID
    if users_service.is_nickname_exists(user_data['nickname']):
        user_data['nickname'] = '%s%s' % (user_data['nickname'][:12], user_id)

    user_table = user_models.get_user_info_table(user_id)
    user_insert_sql = user_table.insert().values(**user_data)
    oauth2_insert_sql = user_models.oauth2_table.insert().values(**oauth2_data)
    nickname = user_data['nickname']
    nickname_index_table = user_models.get_nickname_index_table(nickname.lower())
    nickname_index_sql = nickname_index_table.insert().values(nickname=nickname.lower(), user_id=user_id)
    user_models.exec_change(user_insert_sql, oauth2_insert_sql, nickname_index_sql)

    return jsonify(make_user_info(user_data))


@bp.route('/nickname/check/', methods=['POST'])
def nickname_check():
    ''' 检查昵称的唯一性 '''
    data = user_forms.nickname_check_schema(convert_dict(request.json))
    nickname = data['nickname']

    ret = users_service.is_nickname_exists(nickname)
    return jsonify(dict(nickname_exists=ret))


@bp.route('/oauth2/check/', methods=['POST'])
def oauth2_check():
    data = user_forms.oauth2_check_schema(convert_dict(request.json))
    oauth2_info = users_service.get_oauth2_info(**data)
    return jsonify(oauth2_info)


@bp.route('/verify/', methods=['POST'])
def verify():
    data = user_forms.user_verify_schema(convert_dict(request.json))
    user_id = data['user_id']
    verify_type = data['verify_type']

    # 前置条件检查
    user_info = users_service.get_user_info(user_id)
    if not user_info:
        raise errors.ErrUserNotExist
    if verify_type == 'email' and user_info.email_verified:
        raise errors.ErrEmailVerified
    if verify_type == 'mobile' and user_info.mobile_verified:
        raise errors.ErrMobileVerified

    # 更改认证信息
    update_data = dict()
    if verify_type == 'email':
        data['email_verified'] = True
    elif verify_type == 'mobile':
        data['mobile_verified'] = True

    user_table = user_models.get_user_info_table(user_id)
    update_sql = user_table.update()\
            .where(user_table.c.user_id == user_id)\
            .values(**update_data)
    user_models.exec_change(update_sql)

    return jsonify()


@bp.route('/profile/update/', methods=['POST'])
def update_profile():
    data = user_forms.update_profile_schema(convert_dict(request.json))
    user_id = data.pop('user_id')
    nickname = data.get('nickname')
    sqls = []
    user_info = users_service.get_user_info(user_id)
    if not user_info:
        raise errors.ErrUserNotExist
    if 'username' in data and user_info['username'] != data['username']:
        username = data['username']
        # 用户名不能以 玩家 开头
        if re.match(u"^\u73a9\u5bb6", username):
            raise errors.ErrUsernameIllegal
        # 检查新用户名是否存在
        old_user = users_service.get_user_by_username(username)
        # 新用户名没有被占用
        if not old_user:
            # 非默认用户名
            if user_info['username']:
                old_username_table = user_models.get_username_index_table(user_info['username'])
                username_delete_sql = old_username_table.delete()\
                    .where(old_username_table.c.username == user_info['username'])
                sqls.append(username_delete_sql)
            username_table = user_models.get_username_index_table(username)
            username_insert_sql = username_table.insert()\
                .values(user_id=user_id, username=username)
            sqls.append(username_insert_sql)
        # 新用户名查到的用户不是自己
        elif old_user['user_id'] != user_id:
            raise errors.ErrUsernameExist
    if 'email' in data\
            and data['email'] != user_info['email']\
            and not user_info['email_verified']:
        email = data['email']
        old_user = users_service.get_user_by_email(email)
        if not old_user:
            if user_info['email']:
                old_email_table = user_models.get_email_index_table(user_info['email'])
                email_delete_sql = old_email_table.delete()\
                    .where(old_email_table.c.email == user_info['email'])
                sqls.append(email_delete_sql)
            email_table = user_models.get_email_index_table(email)
            email_insert_sql = email_table.insert()\
                .values(user_id=user_id, email=email)
            sqls.append(email_insert_sql)
        elif old_user['user_id'] != user_id:
            raise errors.ErrEmailExist
    if 'mobile' in data\
            and data['mobile'] != user_info['mobile']\
            and not user_info['mobile_verified']:
        mobile = data['mobile']
        old_user = users_service.get_user_by_mobile(mobile)
        if not old_user:
            if user_info['mobile']:
                old_mobile_table = user_models.get_mobile_index_table(user_info['mobile'])
                mobile_delete_sql = old_mobile_table.delete()\
                    .where(old_mobile_table.c.mobile == user_info['mobile'])
                sqls.append(mobile_delete_sql)
            mobile_table = user_models.get_mobile_index_table(mobile)
            mobile_insert_sql = mobile_table.insert()\
                .values(user_id=user_id, mobile=mobile)
            sqls.append(mobile_insert_sql)
        elif old_user['user_id'] != user_id:
            raise errors.ErrmobileExist

    # 修改昵称：昵称索引表的增删
    if nickname and user_info['nickname'] != nickname:
        if users_service.is_nickname_exists(nickname):
            raise errors.ErrNicknameExist
        ## 删除旧 nickname
        old_nickname = user_info['nickname']  # sdk 用户没有昵称
        if old_nickname:
            old_nickname_index_table = user_models.get_nickname_index_table(old_nickname.lower())
            old_nickname_index_sql = old_nickname_index_table.delete(old_nickname_index_table.c.nickname == old_nickname.lower())
            sqls.append(old_nickname_index_sql)
        ## 添加新 nickname
        nickname_index_table = user_models.get_nickname_index_table(nickname.lower())
        nickname_index_sql = nickname_index_table.insert().values(nickname=nickname.lower(), user_id=user_id)
        sqls.append(nickname_index_sql)
        ## 主播表更新昵称
        master_user_table = user_models.get_master_user_table()
        master_user_sql = master_user_table.update(master_user_table.c.user_id==user_id)\
                            .values(nickname=nickname)
        sqls.append(master_user_sql)

    user_table = user_models.get_user_info_table(user_id)
    update_sql = user_table.update()\
        .where(user_table.c.user_id == user_id)\
        .values(**data)
    sqls.append(update_sql)
    user_models.exec_change(*sqls)

    return jsonify()


@bp.route('/master/')
def master():
    ''' 主播列表 '''
    data = user_forms.master_schema(convert_dict(request.args))
    ret = users_service.get_master(**data)
    master_user_ids = [mu['user_id'] for mu in ret]
    return jsonify({'master_user_ids': master_user_ids})


@bp.route('/forbid/', methods=['POST'])
def forbid():
    '''
    禁用账号
    主播账号不能直接禁用(先降级为普通用户，再禁用)
    '''
    data = user_forms.user_forbid_schema(convert_dict(request.json))
    user_id = data['user_id']

    # 主播用户不能直接禁用
    user_info = users_service.get_user_info(user_id)
    if not user_info or user_info['user_type'] == 2:
        return jsonify({'ret': False})

    ret = users_service.forbid_user(user_id)
    if not ret:
        return jsonify({'ret': False})
    return jsonify({'ret': True})


@bp.route('/unforbid/', methods=['POST'])
def unforbid():
    ''' 解禁账号 '''
    data = user_forms.user_forbid_schema(convert_dict(request.json))
    user_id = data['user_id']

    ret = users_service.unforbid_user(user_id)
    if not ret:
        return jsonify({'ret': False})
    return jsonify({'ret': True})


@bp.route('/follow/', methods=['POST'])
def follow():
    ''' 关注 '''
    data = user_forms.follow_schema(convert_dict(request.json))
    user_id = data['user_id']
    follow_user_id = data['follow_user_id']
    notification = data['notification']

    if user_id == follow_user_id:
        raise errors.ErrInvalidFollow

    if not users_service.get_user_info(user_id):
        raise errors.ErrUserNotExist
    if not users_service.get_user_info(follow_user_id):
        raise errors.ErrFollowUserNotExist

    is_follow = users_service.is_follow(user_id, follow_user_id)
    if is_follow:
        raise errors.ErrHaveFollowed

    users_service.follow_user(user_id=user_id, follow_user_id=follow_user_id, notification=notification)
    user_caches.incr_user_count(user_id, USER.USER_FOLLOW_COUNT)
    user_caches.incr_user_count(follow_user_id, USER.USER_FANS_COUNT)
    try: # 添加虚拟粉丝
        real_fans_users = users_service.get_user_real_fans(follow_user_id)
        vfans_count = gen_vfans_count(len(real_fans_users))
        print "vfans_count :", vfans_count
        if vfans_count:
            fans_users = users_service.get_user_fans(follow_user_id)
            vfans_users = users_service.get_vfans_users(user_id, fans_users,
                                          vfans_count)
            vfans_users = vfans_users or []
            for vfans_user in vfans_users:
                users_service.follow_user(user_id=vfans_user["user_id"],
                                          follow_user_id=follow_user_id,
                                          parent_id=user_id,
                                          notification=notification)
                user_caches.incr_user_count(vfans_user["user_id"],
                                            USER.USER_FOLLOW_COUNT)
                user_caches.incr_user_count(follow_user_id,
                                            USER.USER_FANS_COUNT)
    except Exception,ex:
        print "add virtual fans user :", ex
    return jsonify()


@bp.route('/unfollow/', methods=['POST'])
def unfollow():
    ''' 取消关注 '''
    data = user_forms.follow_schema(convert_dict(request.json))
    user_id = data['user_id']
    follow_user_id = data['follow_user_id']

    if user_id == follow_user_id:
        raise errors.ErrInvalidFollow

    if not users_service.get_user_info(user_id):
        raise errors.ErrUserNotExist
    if not users_service.get_user_info(follow_user_id):
        raise errors.ErrFollowUserNotExist

    is_follow = users_service.is_follow(user_id, follow_user_id)
    if not is_follow:
        raise errors.ErrNotFollowed

    users_service.unfollow_user(user_id=user_id, follow_user_id=follow_user_id)
    user_caches.decr_user_count(user_id, USER.USER_FOLLOW_COUNT)
    user_caches.decr_user_count(follow_user_id, USER.USER_FANS_COUNT)
    try: # 移除虚拟粉丝
        vfans_users = users_service.get_vfans_users_by_parent_id(
                          follow_user_id, user_id)
        print "remove vfans_users len : ", len(vfans_users)
        for vfans_user in vfans_users:
            users_service.unfollow_user(
                user_id = vfans_user["fans_user_id"],
                follow_user_id = follow_user_id)
            user_caches.decr_user_count(vfans_user["fans_user_id"],
                                        USER.USER_FOLLOW_COUNT)
            user_caches.decr_user_count(follow_user_id,
                                        USER.USER_FANS_COUNT)
    except Exception,ex:
        print "remove virtual fans user :", ex
    return jsonify()


@bp.route('/follow/list/')
def follow_list():
    ''' 用户的关注列表 '''
    data = user_forms.follow_list_schema(convert_dict(request.args))

    user_follow_list = users_service.get_user_follow(data['user_id'], offset=data['offset'], limit=data['limit'])
    to_be_deleted = []
    for followed_user in user_follow_list:
        followed_user_info = users_service.get_user_info(followed_user['follow_user_id'])
        if followed_user_info['user_type'] != 2:
            to_be_deleted.append(followed_user)
    for element in to_be_deleted:
        user_follow_list.remove(element)
    return json.jsonify(user_follow_list)


@bp.route('/fans/new/count/', methods=['GET', 'POST'])
def fans_new():
    '''
    用户新增粉丝数，用于当红主播排行榜
    查询用户近 7 天内的新增加粉丝数(不含今天)
    '''
    if request.method == 'POST':
        request.args = request.json
    data = user_forms.user_ids_schema(convert_dict(request.args))
    user_ids = data['user_ids']
    days = 7

    fans_new_counts = dict()
    for user_id in user_ids:
        today_date_str = datetime.now().strftime('%Y-%m-%d')
        start_time = (datetime.now() - timedelta(days)).strftime('%Y-%m-%d') + ' 00:00:00'
        end_time = today_date_str + ' 00:00:00'

        fans_list = users_service.get_user_recent_fans(user_id, start_time, end_time)
        count = len(fans_list)
        fans_new_counts[user_id] = count

    return jsonify(fans_new_counts)

@bp.route("/report/",methods=["POST"])
def report():
    '''举报用户'''
    data = convert_dict(request.json)
    data = user_forms.user_report_schema(data)
    rs = users_service.create_report_user(**data)
    if rs == -1:
        msg = "已举报过"
    elif rs == 0:
        msg = "举报失败"
    else:
        msg = "举报成功"
    return jsonify(dict(msg = msg))

@bp.route("/fans/list/")
def fans_list():
    """ 粉丝列表 """
    data = convert_dict(request.args)
    data = user_forms.fans_list_schema(data)
    user_id = data["user_id"]
    offset, limit = data["offset"], data["limit"]
    fans_users = users_service.get_user_fans(user_id, offset, limit)
    return json.jsonify(fans_users)

@bp.route("/check_follow/")
def check_follow():
    """ 检测是否关注 """
    data = convert_dict(request.args)
    data = user_forms.check_follow_schema(data)
    user_id = data["user_id"]
    follow_user_id = data["follow_user_id"]
    is_followed = users_service.is_follow(user_id = user_id,
                      follow_user_id = follow_user_id)
    return json.jsonify(dict(is_followed = is_followed))


@bp.route('/search/master_users/')
def search_master_users():
    ''' 搜索主播用户 '''
    data = user_forms.search_schema(convert_dict(request.args))
    keyword = data['keyword']

    master_users = users_service.search_master_users(keyword)
    for item in master_users:
        item.pop('is_deleted')
        item.pop('is_recommended')
        item.pop('sort')

    return jsonify(master_users=master_users)


@bp.route('/master_user/room_id/update/', methods=['POST'])
def master_user_room_id_update():
    '''更新主播表的直播间ID
    用途:
        1. 创建直播间时
        2. 直播间ID统一变更时
    '''
    data = user_forms.room_id_update_schema(convert_dict(request.json))
    user_id = data.pop('user_id')
    room_id = data['room_id']

    users_service.update_master_user(user_id, **dict(room_id=room_id))
    return jsonify()


@bp.route('/insert_bank_info/', methods=['POST'])
def insert_bank_info():
    """
    插入或更新一条新的用户银行卡认证纪录
    针对单个用户银行卡认证记录只保留一条
    如果此用户已有银行卡认证记录则更新当前记录
    """
    data = user_forms.insert_bank_info_schema(convert_dict(request.json))
    users_service.insert_bank_info(**data)
    return jsonify()


@bp.route('/get_bank_info/')
def get_bank_info():
    """
    根据用户id查询用户的银行卡认证纪录
    """
    data = user_forms.get_bank_info_schema(convert_dict(request.args))
    user_id = data['user_id']
    return jsonify(users_service.get_bank_info(user_id))


@bp.route('/insert_contract/', methods=['POST'])
def insert_contract():
    """
    根据user_id为某个用户插入新的合约纪录
    """
    data = user_forms.insert_contract_schema(convert_dict(request.json))
    users_service.insert_contract(**data)
    return jsonify()


@bp.route('/get_all_contract/')
def get_all_contract():
    """
    根据user_id获取某个用户的所有合约纪录
    """
    data = user_forms.get_all_contract_schema(convert_dict(request.args))
    user_id = data['user_id']
    resp = users_service.get_all_contract(user_id)
    for r in resp:
        r['start_from'] = r['start_from'].strftime("%Y-%m-%d %H:%M:%S")
    resp = json.dumps(resp)
    return resp


@bp.route('/get_current_contract/')
def get_current_contract():
    """
    根据user_id获取某个用户的当前激活合约
    """
    data = user_forms.get_all_contract_schema(convert_dict(request.args))
    user_id = data['user_id']
    resp = users_service.get_current_contract(user_id)
    resp['start_from'] = resp['start_from'].strftime("%Y-%m-%d %H:%M:%S")
    resp = json.dumps(resp)
    return resp


@bp.route('/get_next_contract/')
def get_next_contract():
    """
    根据user_id获取某个用户的下一个生效的合约
    """
    data = user_forms.get_all_contract_schema(convert_dict(request.args))
    user_id = data['user_id']
    now = datetime.now().strftime('%Y-%m-%d') + ' 00:00:00'
    resp = users_service.get_next_contract(user_id, now)
    resp['start_from'] = resp['start_from'].strftime("%Y-%m-%d %H:%M:%S")
    resp = json.dumps(resp)
    return resp


@bp.route('/notification/modify/')
def notification_on():
    """
    某用户打开接收某主播的开播通知
    """
    data = user_forms.notification_schema(convert_dict(request.args))
    user_id = data['user_id']
    master_user_id = data['master_user_id']

    if user_id == master_user_id:
        raise errors.ErrInvalidFollow

    if not users_service.get_user_info(user_id):
        raise errors.ErrUserNotExist
    if not users_service.get_user_info(master_user_id):
        raise errors.ErrFollowUserNotExist

    is_follow = users_service.is_follow(user_id, master_user_id)
    if not is_follow:
        raise errors.ErrNotFollowed

    modify = data['modify']
    users_service.notification_modify(user_id, master_user_id, modify)
    return jsonify()


@bp.route('/notification/check/')
def notification_check():
    """
    检查某用户当前是否接收某主播的开播通知
    """
    data = user_forms.notification_schema(convert_dict(request.args))
    user_id = data['user_id']
    master_user_id = data['master_user_id']

    if user_id == master_user_id:
        raise errors.ErrInvalidFollow

    if not users_service.get_user_info(user_id):
        raise errors.ErrUserNotExist
    if not users_service.get_user_info(master_user_id):
        raise errors.ErrFollowUserNotExist

    is_follow = users_service.is_follow(user_id, master_user_id)
    if not is_follow:
        raise errors.ErrNotFollowed

    resp = users_service.notification_check(user_id, master_user_id)
    if not resp:
        return json.jsonify(dict(notification=0))
    else:
        return json.jsonify(dict(notification=resp['notification']))


@bp.route('/master/set/')
def master_set():
    """
    将某个用户设置为主播用户
    """
    data = user_forms.user_id_schema(convert_dict(request.args))
    user_id = data['user_id']

    user_info = users_service.get_user_info(user_id)
    if 'user_type' not in user_info:
        raise errors.ErrUserNotExist
    if user_info['user_type'] == 2:
        raise errors.ErrUserAlreadyMaster

    users_service.master_set(user_id)

    room_id_data = room_client.list(user_id=user_id, is_deleted=1)
    if room_id_data == []:
        room_id = 0
    else:
        room_id = room_id_data[0]['id']

    if room_id == 0:
        return jsonify()
    room_client.modify(id=room_id, is_deleted=0)
    return jsonify()


@bp.route('/master/unset/')
def master_unset():
    """
    将某个用户的主播资格撤销
    """
    data = user_forms.user_id_schema(convert_dict(request.args))
    user_id = data['user_id']

    user_info = users_service.get_user_info(user_id)
    if 'user_type' not in user_info:
        raise errors.ErrUserNotExist
    if user_info['user_type'] != 2:
        raise errors.ErrUserNotMaster

    users_service.master_unset(user_id)

    room_id_data = room_client.list(user_id=user_id)
    if room_id_data == []:
        room_id = 0
    else:
        room_id = room_id_data[0]['id']

    if room_id == 0:
        return jsonify()
    room_client.modify(id=room_id, is_deleted=1)
    return jsonify()
