# -*- coding: utf-8 -*-

from voluptuous import Schema, All, Required, Match, Length, Range, In, Coerce, Datetime

from tlutil.validator import to_strip, to_split
from tlutil.validator import email_validator, ipv4_validator, tfsUrl_validator, nickname_validator


user_id_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=10001))
})


user_ids_schema = Schema({
    Required('user_ids'): All(Coerce(to_split), Range(min=10001))
})


mobile_register_schema = Schema({
    Required('mobile'): All(unicode, Length(min=11, max=15)),
    Required('nickname'): All(Coerce(unicode), Length(min=2, max=20), Match(nickname_validator)),
    Required('password'): All(unicode, Length(min=6, max=20)),
    Required('platform'): All(Coerce(int), Range(min=0, max=3)),
    Required('user_ip'): All(unicode, Match(ipv4_validator)),
    # f(female)表示女性，m(male)表示男性，u(unkown)表示未知
    Required('gender', default='u'): In(frozenset(['f', 'm', 'u'])),
    Required('cover', default=''): All(unicode),
    Required('avatar', default=''): All(unicode),
    Required('channel', default=''): All(unicode),
})

email_register_schema = Schema({
    Required('email'): All(unicode, Length(min=5, max=30), Match(email_validator)),
    Required('password'): All(unicode, Length(min=6, max=20)),
    Required('platform'): All(Coerce(int), Range(min=1, max=3)),
    Required('user_ip'): All(unicode, Match(ipv4_validator)),
    Required('gender', default='u'): In(frozenset(['f', 'm', 'u'])),
})

device_register_schema = Schema({
    Required('device_hash'): All(unicode, Length(32)),
    'imei': All(unicode, Length(min=6, max=30)),
    Required('user_ip'): All(unicode),
    Required('platform'): All(Coerce(int), Range(min=1, max=3)),
    Required('cover', default=''): All(unicode),
    Required('avatar', default=''): All(unicode),
    Required('gender', default='u'): In(frozenset(['f', 'm', 'u'])),
    'device_info': All(unicode),
    'channel': All(unicode),
})

nickname_check_schema = Schema({
    Required('nickname'): All(Coerce(unicode), Length(min=2, max=20)),
})

user_query_schema = Schema({
    Required('type'): In(frozenset(['username', 'email', 'mobile', 'device_hash'])),
    Required('value'): All(unicode),
})

nickname_change_schema = Schema({
    Required('user_id'): All(int, Range(min=1)),
    Required('nickname'): All(Coerce(unicode), Length(min=2, max=20), Coerce(to_strip)),
})

password_change_schema = Schema({
    Required('user_id'): All(int, Range(min=1)),
    Required('old_password'): All(unicode, Length(min=6, max=20)),
    Required('new_password'): All(unicode, Length(min=6, max=20)),
})

password_reset_schema = Schema({
    Required('user_id'): All(int, Range(min=1)),
    Required('new_password'): All(unicode, Length(min=6, max=20)),
})

avatar_change_schema = Schema({
    Required('user_id'): All(int, Range(min=1)),
    Required('new_avatar'): All(unicode),
})

cover_change_schema = Schema({
    Required('user_id'): All(int, Range(min=1)),
    Required('new_cover'): All(unicode),
})

user_auth_schema = Schema({
    'user_id': All(int, Range(min=1)),
    'username': All(Coerce(unicode), Length(min=2, max=20), Coerce(to_strip)),
    'email': All(unicode, Length(min=5, max=30), Match(email_validator)),
    'mobile': All(unicode, Length(min=11, max=15)),
    Required('password'): All(unicode, Length(min=6, max=20)),
})

user_verify_schema = Schema({
    Required('user_id'): All(int, Range(min=1)),
    Required('type'): In(frozenset(['email', 'mobile'])),
})


oauth2_check_schema = Schema({
    Required('open_id'): All(Coerce(unicode), Length(min=5, max=50)),
    Required('channel'): In(frozenset(['weibo', 'weixin', 'qq'])),
    Required('platform'): All(Coerce(int), Range(min=0, max=3)),
})


oauth2_register_schema = Schema({
    Required('open_id'): All(Coerce(unicode), Length(min=5, max=50)),
    Required('channel'): In(frozenset(['weibo', 'weixin', 'qq'])),
    Required('platform'): All(Coerce(int), Range(min=0, max=3)),
    #Required('nickname'): All(Coerce(unicode), Length(min=2, max=20), Match(nickname_validator)),
    Required('nickname'): All(Coerce(unicode), Length(min=1, max=20)),
    Required('user_ip'): All(unicode, Match(ipv4_validator)),
    Required('gender', default='u'): In(frozenset(['f', 'm', 'u'])),
    Required('from', default=''): All(unicode),
    #'avatar': All(str, Match(tfsUrl_validator)),
    'avatar': All(Coerce(str), Length(min=1)),
})


update_profile_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    'username': All(Coerce(unicode), Length(min=2, max=20), Coerce(to_strip)),
    'nickname': All(Coerce(unicode), Length(min=2, max=20), Match(nickname_validator)),
    # f(female)表示女性，m(male)表示男性，u(unkown)表示未知
    'email': All(unicode, Length(min=5, max=30), Match(email_validator)),
    'mobile': All(unicode, Length(min=11, max=15)),
    'gender': In(frozenset(['f', 'm'])),
    'birthday': All(unicode),
    'status_text': All(unicode),
    'qq': All(unicode),
    'avatar': All(Coerce(str), Length(min=1)),
})

master_schema = Schema({
    Required('offset', default=0): All(Coerce(int), Range(min=0)),
    Required('limit', default=10): All(Coerce(int), Range(min=-1)),
})

follow_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    Required('follow_user_id'): All(Coerce(int), Range(min=1)),
    Required('notification', default=1): All(Coerce(int), Range(min=0, max=1)),
})

follow_list_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    Required('offset', default=0): All(Coerce(int), Range(min=0)),
    Required('limit', default=10): All(Coerce(int), Range(min=-1)),
})

user_forbid_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=10001))
})

user_report_schema = Schema({
    Required("reported_uid"): All(Coerce(int), Range(min=10001)),
    Required("user_id"): All(Coerce(int), Range(min=10001)),
    Required("report_type", default=0): All(Coerce(int), Range(min=0,max=1)),
})

fans_list_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    Required('offset', default=0): All(Coerce(int), Range(min=0)),
    Required('limit', default=10): All(Coerce(int), Range(min=-1)),
})

check_follow_schema = Schema({
    Required("user_id"): All(Coerce(int), Range(min=1)),
    Required("follow_user_id"): All(Coerce(int), Range(min=1)),
})

user_id_query_schema = Schema({
    'nickname': All(Coerce(unicode), Length(min=1)),
    'mobile': All(unicode, Length(min=11, max=15)),
})

search_schema = Schema({
    Required('keyword'): All(Coerce(unicode), Length(min=1)),
})

room_id_update_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    Required('room_id'): All(Coerce(int), Range(min=1)),
})

insert_bank_info_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    Required('card_num'): All(Coerce(unicode), Length(min=1)),
    Required('bank_name'): All(Coerce(unicode), Length(min=1)),
    Required('card_holder'): All(Coerce(unicode), Length(min=1)),
})

get_bank_info_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
})

insert_contract_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    Required('contract_type'): All(Coerce(int), Range(min=0, max=2)),
    Required('rank_reward_bonus_rate'): All(Coerce(float), Range(min=0.0, max=1.0)),
    Required('basic_salary', default=0): All(Coerce(int), Range(min=0)),
    Required('gift_exponent_share', default=0.5): All(Coerce(float), Range(min=0.0)),
    Required('start_from'): All(Coerce(Datetime('%Y-%m-%d %H:%M:%S'))),
})

get_all_contract_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
})

notification_schema = Schema({
    Required('user_id'): All(Coerce(int), Range(min=1)),
    Required('master_user_id'): All(Coerce(int), Range(min=1)),
    'modify': All(Coerce(int), Range(min=0, max=1)),
})