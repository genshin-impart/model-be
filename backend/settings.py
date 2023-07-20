# -*- coding: utf-8 -*-
import os
import sys

USERNAME_LEN = 32

basedir = os.path.abspath(os.path.dirname(__file__))

# SQLite URL compatible
prefix = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'


class BaseConfig:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')


class DevelopmentConfig(BaseConfig):
    """开发配置"""
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'redis://localhost'


class TestingConfig(BaseConfig):
    """测试配置"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' # in-memory database
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(BaseConfig):
    """部署配置"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}