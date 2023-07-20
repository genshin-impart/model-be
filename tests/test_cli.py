# -*- coding: utf-8 -*-
import sys
import unittest

sys.path.append('..')

from backend.models import Admin, User, PaddleModel, BindingModel
from backend.extensions import db

from base import BaseTestCase


class CLITestCase(BaseTestCase):
    """命令行测试用例"""

    def setUp(self):
        super(CLITestCase, self).setUp()
        with self.app.app_context():
            db.drop_all()

    def test_initdb_command(self):
        result = self.runner.invoke(args=['initdb'])
        self.assertIn('Initialized database.', result.output)

    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(args=['initdb', '--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)


if __name__ == '__main__':
    unittest.main()