# -*- coding: utf-8 -*-
import sys
import unittest

from flask import url_for

sys.path.append('..')

from backend.app import create_app
from backend.extensions import db
from backend.models import Admin


class BaseTestCase(unittest.TestCase):
    """测试基类"""

    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.test_request_context()
        self.context.push()
        self.client = self.app.test_client()
        self.runner = self.app.test_cli_runner()
        with self.app.app_context():
            db.create_all()
            user = Admin(username='hust')
            user.set_password('hust')
            db.session.add(user)
            db.session.commit()

    def tearDown(self) -> None:
        with self.app.app_context():
            db.drop_all()
        self.context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'hust'
            password = 'hust'

        return self.client.post(
            url_for('user.login'), data=dict(username=username, password=password), follow_redirects=True
        )

    def logout(self):
        return self.client.post(url_for('user.logout'), follow_redirects=True)


if __name__ == '__main__':
    unittest.main()