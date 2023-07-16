# -*- coding: utf-8 -*-
# from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_cors import CORS

# * 数据库配置
db = SQLAlchemy()

# * Session 配置
sess = Session()

# * SocketIO 配置
# my_socketio = SocketIO()

# * 垮域配置
# cors = CORS(resources={"*": {"origins": "*"}})
cors = CORS(resources=r'/*')