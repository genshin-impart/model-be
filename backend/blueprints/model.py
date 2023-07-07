# -*- coding: utf-8 -*-
import os

from flask import redirect, request, url_for, abort, jsonify, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from backend.models import PaddleModel
from backend.extensions import db

import backend.utils.create as c_utils
import backend.utils.model as m_utils

model_bp = Blueprint('model', __name__)


@model_bp.route('/list', methods=['GET'])
def fetch_model_list():
    page_size = int(request.args['pageSize'])
    page_num = int(request.args['pageNum'])
    # ? DEBUG
    print("page_size: {}\npage_num: {}".format(page_size, page_num))
    # TODO 返回 PaddleModel 的相关信息
    model_list = m_utils.get_all_models()
    # ? DEBUG
    print("model_list:\n", model_list)
    return jsonify()


@model_bp.route('/choose', methods=['POST'])
def choose_model():
    model_id = int(request.args['id'])
    # ? DEBUG
    print("choose model id: {}".format(model_id))
    # TODO 在 PaddleModel 中选中模型
    pass
    return jsonify()


@model_bp.route('/fileUpload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    assert (file is not None)
    # ? DEBUG
    print("filename: {}".format(file.filename))
    # TODO 保存文件到缓存路径
    pass
    return jsonify()


@model_bp.route('/fileRemove', methods=['POST'])
def remove_file():
    file_id = request.args['id']
    # ? DEBUG
    print("file_id: {}".format(file_id))
    # TODO 从缓存路径中删除文件
    pass
    return jsonify()


@model_bp.route('/apply', methods=['POST'])
def apply_model():
    request_args = request.args.get()
    # ? DEBUG
    print("request_args: {}".format(request_args))
    # TODO
    pass
    return jsonify()


@model_bp.route('/create', methods=['POST'])
def create_model():
    # TODO websocket.io 通信
    pass
    return jsonify()