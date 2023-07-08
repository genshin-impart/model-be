# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
coredir = os.path.join(basedir, 'model-core')


def init_env():
    print('Init venv environment')
    


if __name__ == '__main__':
    init_env()