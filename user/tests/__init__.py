# -*- coding: utf-8 -*-

from unittest import TestCase

from .utils import FlaskTestCaseMixin


class TestCase(TestCase):
    pass


class AppTestCase(FlaskTestCaseMixin, TestCase):

    def _create_app(self):
        raise NotImplementedError

    def setUp(self):
        super(AppTestCase, self).setUp()
        self.app = self._create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        super(AppTestCase, self).tearDown()
        self.app_context.pop()
