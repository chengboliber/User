# -*- coding: utf-8 -*-

from . import ApiTestCase


class UserApiTestCase(ApiTestCase):

    def test_query_profile(self):
        rv = self.get('/user/profile/?user_id=10192')
        self.assertOk(rv)

    def test_query_profile_bulk(self):
        rv = self.get('/user/profile/bulk/?user_ids=10192,10193')
        self.assertOk(rv)

    def test_query_profile_not_exist(self):
        rv = self.get('/user/profile/?user_id=10008')
        self.assertBadRequest(rv)

    def test_query_by_username(self):
        data = {'type': 'username', 'value': 'zeayes01'}
        rv = self.post('/user/query/', data=data)
        self.assertOk(rv)

    def test_query_by_mobile(self):
        data = {'type': 'mobile', 'value': '18566206365'}
        rv = self.post('/user/query/', data=data)
        self.assertOk(rv)

    def test_query_by_email(self):
        data = {'type': 'email', 'value': 'zeayes@qq.com'}
        rv = self.post('/user/query/', data=data)
        self.assertOk(rv)
