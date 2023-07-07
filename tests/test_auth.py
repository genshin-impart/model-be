# -*- coding: utf-8 -*-
import sys
import unittest
from flask import url_for

sys.path.append('..')

from base import BaseTestCase


class AuthTestCase(BaseTestCase):

    def test_login_user(self):
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('Welcome back.', data)

    def test_fail_login(self):
        response = self.login(username='wrong-username', password='wrong-password')
        data = response.get_data(as_text=True)
        self.assertIn('Invalid username of password.', data)

    def test_logout_user(self):
        self.login()
        response = self.logout()
        data = response.get_data(as_text=True)
        self.assertIn('Logout success.', data)

    # def test_login_protect(self):
    #     response = self.client.get(url_for('admin.settings'), follow_redirects=True)
    #     data = response.get_data(as_text=True)
    #     self.assertIn('Please log in to access this page.', data)


if __name__ == '__main__':
    unittest.main()