# -*- coding: utf-8 -*-
from flask import redirect, request, url_for, abort, jsonify, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from utils.auth import get_user

user_bp = Blueprint('user', __name__)


@user_bp.route('/login', methods=['POST'])
def login():
    # assert (not current_user.is_authenticated)
    user_name = request.json.get('username')
    pwd_hash = request.json.get('password')
    # ? DEBUG
    print('--------------------')
    print('username: {}\npwd_hash: {}'.format(user_name, pwd_hash))
    print('--------------------')
    # TODO pwd 解密
    user = get_user(user_name)
    if user is None:
        pass
    # TODO check password
    pass
    # TODO login user
    # login_user(user)
    return jsonify({'code': 0, 'msg': 'login success', 'data': user_name})


@user_bp.route('/logout', methods=['POST'])
def logout():
    # user_name = current_user.username
    # TODO logout user
    # logout_user()
    pass
    return jsonify({'code': 0, 'msg': 'logout success', 'data': "hhh"})