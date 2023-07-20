# -*- coding: utf-8 -*-
import unittest

from flask import current_app

from base import BaseTestCase


class BasicTestCase(BaseTestCase):
    """基础测试用例"""

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_404_error(self):
        response = self.client.get('/foo')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('404 Not Found', data)


if __name__ == '__main__':
    unittest.main()