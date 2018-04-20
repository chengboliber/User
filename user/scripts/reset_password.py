# _*_ coding: utf_8 _*_

import os
import sys

_basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

from user.helpers import encrypt_password

from user import users as users_service

user_info = users_service.get_user_id_by_username('zeayes01')
print user_info
users_service.update_password(user_info['user_id'], encrypt_password('123456'))
