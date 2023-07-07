# -*- coding: utf-8 -*-
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import Admin, User, PaddleModel, BindingModel

fake = Faker()


def fake_admin():
    admin = Admin(username='admin')
    db.session.add(admin)
    db.session.commit()


def fake_users():
    user1 = User(username='clzh')
    user1.set_password('123456')

    user2 = User(username='zjy')
    user2.set_password('123456')

    user3 = User(username='wdh')
    user3.set_password('654321')

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()


def fake_models():
    model1 = PaddleModel(
        description='simple model 1', # name
        in_chunk_len=32,
        out_chunk_len=32,
    )

    model2 = PaddleModel(
        description='simple model 2', # name
        in_chunk_len=192,
        out_chunk_len=96,
        batch_size=64,
        learning_rate=5e-3
    )

    db.session.add(model1)
    db.session.add(model2)
    db.session.commit()


def fake_bindings():
    pass