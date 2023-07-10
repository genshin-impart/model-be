# -*- coding: utf-8 -*-
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()
sess = Session()