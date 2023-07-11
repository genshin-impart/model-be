# -*- coding: utf-8 -*-
import os

from flask import redirect, request, url_for, abort, jsonify, session, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from backend.models import PaddleModel
from backend.extensions import db, sess

import backend.utils.create as c_utils
import backend.utils.model as m_utils
import backend.utils.file as f_utils
import backend.utils.core as core_utils

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
    print('====================')
    print("model_list:\n", model_list)
    print("length of model_info_list: ", len(model_info_list))
    print("model_info_list:\n", model_info_list)
    print('====================')
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
    assert (file is not None) # TODO 完成后删除
    # ? DEBUG
    print("filename: {}".format(file.filename))
    # 保存文件到缓存路径
    return_code, file_uuid, cache_file_path = f_utils.cache_file(file)
    file_columns = f_utils.get_file_columns(cache_file_path)
    preview_data = f_utils.preview_data(cache_file_path)
    merged_data = f_utils.preview_data(cache_file_path)
    if return_code == 1: # 重复文件，从 file_to_uuid 索引表中获取
        file_uuid = file_to_uuid[file.filename]
    session['file_uuid'] = file_uuid
    # TODO 判断当前数据集是否存在
    if session.get('set_uuid', 'unknown') == 'unknown':
        # 不存在，创建新的数据集
        new_dset = f_utils.create_dset()
        session['set_uuid'] = new_dset.uuid
        f_utils.merge_file_to_dset(cache_file_path, new_dset.data_path)
    else:
        # 存在，合并当前文件到数据集
        cur_dset = f_utils.get_dset(session['set_uuid'])
        if cur_dset is None:
            print("Dataset not found!")
        else:
            f_utils.merge_file_to_dset(cache_file_path, cur_dset.data_path)
    response_data = {
        'fileId': file_uuid,
        'setId': session['set_uuid'],
        'columns': file_columns,
        'preview': preview_data,
        'merged': merged_data,  # TODO 暂定同 preview 字段
    }
    print('====================')
    print('return_code: ', return_code)
    print('file_uuid: ', file_uuid)
    print('====================')
    if return_code == 0:
        update_map(file_uuid, file.filename)
        print('====================')
        print('file_to_uuid:\n', file_to_uuid)
        print('====================')
        return jsonify({'code': 0, 'msg': 'success', 'data': response_data})
    elif return_code == 1:
        print('====================')
        print('file_to_uuid:\n', file_to_uuid)
        print('====================')
        return jsonify({'code': 1, 'msg': 'duplicated file', 'data': response_data})
    else:
        return jsonify({'code': -1, 'msg': 'failed', 'data': {}})


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
    set_id = str(request.args['setId'])
    params_dict = dict(request.args['params'])
    model_config_dict = {
        'in_chunk_len': params_dict['inWindowSize'],
        'out_chunk_len': params_dict['outWindowSize'],
        'epoch': params_dict['epochs'], # TODO 添加模型接口
        'batch_size': params_dict['batchSize'],
        'learning_rate': params_dict['learningRate'],
    }
    core_utils.create_and_train_model(set_id, model_config_dict)
    return jsonify({'code': -2, 'msg': 'not implement', 'data': None})