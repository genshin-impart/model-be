# -*- coding: utf-8 -*-
import os
from enum import Enum
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from backend.settings import *
from backend.extensions import db


class Admin(db.Model):
    """ 管理员 """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USERNAME_LEN), unique=True, default='admin')
    pwd_hash = db.Column(db.String(128))

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)
        self.set_password()

    # ? DEBUG
    def desc(self):
        print('------------------------------')
        print('Admin    | ', self.id)
        print('username | ', self.username)
        print('pwd_hash | ', self.pwd_hash)
        print('------------------------------')

    def set_password(self, password: str = 'admin'):
        self.pwd_hash = generate_password_hash(password)


class User(UserMixin, db.Model):
    """ 用户 """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USERNAME_LEN), unique=True)
    pwd_hash = db.Column(db.String(128))

    # ? DEBUG
    def desc(self):
        print('------------------------------')
        print('User     | ', self.id)
        print('username | ', self.username)
        print('pwd_hash | ', self.pwd_hash)
        print('------------------------------')

    # ? Self methods
    def set_username(self, username: str):
        self.username = username

    def set_password(self, password: str):
        self.pwd_hash = generate_password_hash(password)

    def validate_password(self, password: str):
        return check_password_hash(self.pwd_hash, password)

    # ? Relation methods

    def generate_new_binding(self):
        # TODO 参数列表
        pass


class PaddleModel(db.Model):
    """ 模型 """
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128))
    in_chunk_len = db.Column(db.Integer)
    out_chunk_len = db.Column(db.Integer)
    batch_size = db.Column(db.Integer, default=32)
    learning_rate = db.Column(db.Float, default=1e-3)

    # TODO 模型参数字段设计

    def __init__(self, **kwargs):
        super(PaddleModel, self).__init__(**kwargs)

    # ? DEBUG
    def desc(self):
        print('------------------------------')
        print('PaddleModel    | ', self.id)
        print('description    | ', self.description)
        print('in_chunk_len   | ', self.in_chunk_len)
        print('out_chunk_len  | ', self.out_chunk_len)
        print('batch_size     | ', self.batch_size)
        print('learning_rate  | ', self.learning_rate)
        print('------------------------------')


class BindingModel(db.Model):
    """ 绑定了数据的模型 """
    id = db.Column(db.Integer, primary_key=True)
    data_path = db.Column(db.String(64), nullable=False) # 数据路径不可为空
    data_cols = db.Column(db.PickleType)
    status = db.Column(db.Integer)

    # * status 定义
    class ModelStatus(Enum):
        READY = 1
        TRAIN = 2
        FINISH = 3

    model_status = {1: 'READY', 2: 'TRAIN', 3: 'FINISH'}

    # * BindingModel ~ User: n ~ 1
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # * BindingModel ~ PaddleModel: n ~ 1
    model_id = db.Column(db.Integer, db.ForeignKey('paddle_model.id'))

    def __init__(self, user_id: int, model_id: int, data_path: str):
        super(BindingModel, self).__init__()
        self.user_id = user_id
        self.model_id = model_id
        self.status = BindingModel.ModelStatus.READY
        if not os.path.isdir(data_path):
            raise "invalid data path!"
        self.data_path = data_path

    # ? DEBUG
    def desc(self):
        print('------------------------------')
        print('Binding   | ' % self.id)
        print('data_path | ', self.data_path)
        print('data_cols | ', self.data_cols)
        print('status    | ', BindingModel.model_status[self.status])
        print('***** foreign keys *****')
        print('user_id   | ', self.user_id)
        print('model_id  | ', self.model_id)
        print('------------------------------')

    def set_status(self, status):
        if status not in BindingModel.ModelStatus:
            raise "invalid binding status!"
        self.status = status

    def reset_datapath(self, new_datapath: str):
        if not os.path.isdir(new_datapath):
            raise "invalid new data path!"
        self.data_path = new_datapath

    def model_train(self):
        if self.status != BindingModel.ModelStatus.READY:
            raise "model has been trained before!"
        pass

    def model_predict(self):
        if self.status != BindingModel.ModelStatus.FINISH:
            raise "model is not ready for prediction!"
        pass