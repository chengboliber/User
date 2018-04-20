# -*- coding: utf-8 -*-

from . import ApiTestCase


class AuthApiTestCase(ApiTestCase):

    def test_user_id_auth(self):
        data = {
            'user_id': 10193,
            'password': '123456'
        }
        rv = self.post('/user/auth/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_username_auth(self):
        data = {
            'username': 'zeayes01',
            'password': '123456'
        }
        rv = self.post('/user/auth/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_mobile_auth(self):
        data = {
            'mobile': '18566206365',
            'password': '123456'
        }
        rv = self.post('/user/auth/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_email_auth(self):
        data = {
            'email': 'zeayes@qq.com',
            'password': '123456'
        }
        rv = self.post('/user/auth/', data=data)
        print rv.data
        self.assertOk(rv)
