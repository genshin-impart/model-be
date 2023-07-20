# -*- coding: utf-8 -*-
import sys
import unittest

from flask import url_for

sys.path.append('..')

from backend.models import User, PaddleModel, BindingModel
from backend.extensions import db

from base import BaseTestCase


class AdminTestCase(BaseTestCase):
    """管理员测试用例"""

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.login()


if __name__ == '__main__':
    unittest.main()