# -*- coding: utf-8 -*-
from flask import redirect, request, url_for, abort, jsonify, Blueprint, session
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, sess
from utils.auth import get_user

user_bp = Blueprint('user', __name__)


@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    username = request.json.get('username')
    password = request.json.get('password')
    # ? DEBUG
    print('--------------------')
    print('username: ', username)
    print('password: ', password)
    print('--------------------')
    # get user
    user = get_user(username)
    if user is None:
        print(f'user {username} not found!')
        return jsonify({'code': 1, 'msg': 'user not found', 'data': username})
    # check password
    if not user.validate_password(password):
        print(f'user {username} password error!')
        return jsonify({'code': 1, 'msg': 'password error', 'data': username})
    # login user
    login_user(user)
    return jsonify({'code': 0, 'msg': 'login success', 'data': username})


@user_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    # logout user
    logout_user()
    # clear session
    session.clear()
    return jsonify({'code': 0, 'msg': 'logout success', 'data': "hhh"})