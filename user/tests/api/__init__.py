# -*- coding: utf-8 -*-

from user.api import create_app

from .. import AppTestCase, settings


class ApiTestCase(AppTestCase):

    def _create_app(self):
        return create_app(settings)

    def setUp(self):
        super(ApiTestCase, self).setUp()
