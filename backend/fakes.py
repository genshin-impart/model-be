# -*- coding: utf-8 -*-
import os
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Admin, User, PaddleModel, BindingModel

basedir = os.path.abspath((os.path.dirname(__file__)))
coredir = os.path.join(basedir, 'core')
modeldir = os.path.join(coredir, 'model')

fake = Faker()


def fake_admin():
    admin = Admin(username='admin')
    db.session.add(admin)
    db.session.commit()


def fake_users():
    admin_user = User(username='admin')
    admin_user.set_password('admin')

    user1 = User(username='clzh')
    user1.set_password('123456')

    user2 = User(username='zjy')
    user2.set_password('123456')

    user3 = User(username='wdh')
    user3.set_password('654321')

    db.session.add(admin_user)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()


def fake_models():
    # TODO 添加 storage_path 字段
    model1 = PaddleModel(
        name='LSTM model',
        description='LSTM 单模型',
        in_chunk_len=192,
        out_chunk_len=96,
        batch_size=32,
        learning_rate=5e-3,
    )
    model2 = PaddleModel(
        name='LSTM ensemble model',
        description='LSTM 集成模型',
        in_chunk_len=96,
        out_chunk_len=48,
        batch_size=64,
    )
    # 使用 11.csv 生成的模型，用于测试 apply 功能
    model3 = PaddleModel(
        name='11.csv model',
        description='11 号风机集成模型',
        in_chunk_len=172,
        out_chunk_len=172,
        batch_size=32,
        storage_path=os.path.join(modeldir, 'model_of_11')
    )

    db.session.add(model1)
    db.session.add(model2)
    db.session.add(model3)
    db.session.commit()


def fake_bindings():
    pass


if __name__ == '__main__':
    print("basedir: ", basedir)