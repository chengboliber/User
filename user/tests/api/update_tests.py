# -*- coding: utf-8 -*-

from . import ApiTestCase


class UpdateApiTestCase(ApiTestCase):

    def test_cover_change(self):
        data = {
            'user_id': 10193,
            'new_cover': 'tfs/xxxxx.jpg',
        }
        rv = self.post('/user/cover/change/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_avatar_chanage(self):
        data = {
            'user_id': 10193,
            'new_avatar': 'tfs/xxxxx.jpg',
        }
        rv = self.post('/user/avatar/change/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_change_password(self):
        data = {
            'user_id': 10193,
            'new_password': '123456',
            'old_password': '123456'
        }
        rv = self.post('/user/password/change/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_reset_password(self):
        data = {
            'user_id': 10193,
            'new_password': '123456',
        }
        rv = self.post('/user/password/reset/', data=data)
        print rv.data
        self.assertOk(rv)

    def test_update_profile(self):
        data = {
            'user_id': 10193,
            'nickname': 'zeayesli',
        }
        rv = self.post('/user/profile/update/', data=data)
        print rv.data
        self.assertOk(rv)
