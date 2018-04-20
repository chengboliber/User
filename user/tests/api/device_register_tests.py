# -*- coding: utf-8 -*-

import random
import hashlib

from . import ApiTestCase


class RegisterApiTestCase(ApiTestCase):

    def test_device_register(self):
        data = {
            'device_hash': hashlib.md5('zeayes').hexdigest(),
            'imei': ''.join([str(random.choice(range(10))) for i in range(15)]),
            'platform': 1,
            'device_info': 'iphone 5 ios8.1',
            'user_ip': '127.0.0.1',
        }
        rv = self.post('/user/device/register/', data=data)
        self.assertOk(rv)
