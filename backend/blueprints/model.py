# -*- coding: utf-8 -*-
import os

from flask import redirect, request, url_for, abort, jsonify, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from backend.models import PaddleModel
from backend.extensions import db

import backend.utils.create as c_utils
import backend.utils.model as m_utils
import backend.utils.file as f_utils

model_bp = Blueprint('model', __name__)

# * UUID --> cached filename
uuid_to_file = {}
# * cached filename --> uuid
file_to_uuid = {}


def update_map(uuid, filename: str, remove: bool = False):
    if remove:     # 删除
        uuid_to_file.pop(uuid)
        file_to_uuid.pop(filename)
    else:          # 新增
        uuid_to_file[uuid] = filename
        file_to_uuid[filename] = uuid


@model_bp.route('/list', methods=['GET'])
def fetch_model_list():
    page_size = int(request.args['pageSize'])
    page_num = int(request.args['pageNum'])
    # ? DEBUG
    print('====================')
    print(request.url)
    print("page_size: {}\npage_num: {}".format(page_size, page_num))
    print('====================')
    # 返回 PaddleModel 的相关信息
    model_list = m_utils.get_all_models()
    model_info_list = [model.desc(verbose=False) for model in model_list]
    # ? DEBUG
    print("model_list:\n", model_list)
    print("length of model_info_list: ", len(model_info_list))
    return jsonify({'code': 0, 'msg': 'success', 'data': model_info_list})


@model_bp.route('/choose', methods=['POST'])
def choose_model():
    model_id = int(request.args['id'])
    # ? DEBUG
    print("choose model id: {}".format(model_id))
    # TODO 在 PaddleModel 中选中模型
    pass
    return jsonify({'code': -2, 'msg': 'not implement', 'data': None})


@model_bp.route('/fileUpload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    assert (file is not None)
    # ? DEBUG
    print("filename: {}".format(file.filename))
    # 保存文件到缓存路径
    return_code, file_uuid = f_utils.cache_file(file)
    if return_code == 0:
        update_map(file_uuid, file.filename)
        return jsonify({'code': 0, 'msg': 'success', 'uuid': file_uuid})
    elif return_code == 1:
        return jsonify({'code': 1, 'msg': 'duplicated file', 'uuid': file_to_uuid[file.filename]})
    else:
        return jsonify({'code': -1, 'msg': 'failed', 'uuid': ''})


@model_bp.route('/fileRemove', methods=['POST'])
def remove_file():
    file_id = request.args['id']
    # ? DEBUG
    print("file_id: {}".format(file_id))
    # TODO 从缓存路径中删除文件
    pass
    return jsonify({'code': -2, 'msg': 'not implement', 'data': None})


@model_bp.route('/apply', methods=['POST'])
def apply_model():
    request_args = request.args.get()
    # ? DEBUG
    print("request_args: {}".format(request_args))
    # TODO
    pass
    return jsonify({'code': -2, 'msg': 'not implement', 'data': None})


@model_bp.route('/create', methods=['POST'])
def create_model():
    # TODO websocket.io 通信
    pass
    return jsonify({'code': -2, 'msg': 'not implement', 'data': None})