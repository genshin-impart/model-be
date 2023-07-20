# -*- coding: utf-8 -*-
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_socketio import SocketIO
from flask_cors import CORS

# * 用户认证
login_manager = LoginManager()
login_manager.login_view = 'login'

# * 数据库配置
db = SQLAlchemy()

# * Session 配置
sess = Session()

# * SocketIO 配置
my_socketio = SocketIO()

# * 垮域配置
cors = CORS(resources=r'/*')


@login_manager.user_loader
def load_user(user_id):
    from models import User
    user = User.query.get(int(user_id))
    return user