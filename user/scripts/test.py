# _*_ coding: utf_8 _*_

import os
import sys
import requests

from tlutil.json import jsonify

_basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

data = {'user_id': 10001, 'follow_user_id': 10011}
headers = {'Content-Type': 'application/json'}
data = {'user_id': '10264', 'room_id': '0'}

url = 'http://localhost:6100/user/master_user/room_id/update/'

response = requests.post(url=url, data=jsonify(data), headers=headers)
###print response.status_code
print response.content
