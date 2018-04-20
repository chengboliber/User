# -*- coding: utf-8 -*-

import random
import hashlib

from . import ApiTestCase


class RegisterApiTestCase(ApiTestCase):

    def test_device_register(self):
        data = {
            'device_hash': hashlib.md5().hexdigest(),
            'imei': ''.join([str(random.choice(range(10))) for i in range(15)]),
            'platform': 1,
            'device_info': 'iphone 5 ios8.1',
            'user_ip': '127.0.0.1',
        }
        rv = self.post('/user/device/register/', data=data)
        self.assertOk(rv)

    def test_mobile_register(self):
        data = {
            'mobile': '18566206362',
            'nickname': 'zeayes01',
            'password': '123456',
            'platform': 1,
            'user_ip': '127.0.0.1',
            'avatar': 'sys/avatar/0/m.png',
            'cover': 'sys/cover/0/m.png',
        }
        rv = self.post('/user/mobile/register/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_email_register(self):
        data = {
            'email': 'liyao@youxituoluo.com',
            'password': '123456',
            'platform': 1,
            'user_ip': '127.0.0.1',
        }
        rv = self.post('/user/email/register/', data=data)
        print rv.data
        self.assertOk(rv)
