# -*- coding: utf-8 -*-
import os

from flask import request, jsonify, session, Blueprint, send_file
from flask_login import login_user, logout_user, login_required, current_user

import utils.model as m_utils
import utils.file as f_utils

model_bp = Blueprint('model', __name__)

# * UUID --> cached filename
uuid_to_file = {}
# * cached filename --> uuid
file_to_uuid = {}

blueprints_dir = os.path.dirname(__file__)
cache_dir = os.path.join(os.path.dirname(blueprints_dir), 'cache')


def update_map(uuid, filename: str, remove: bool = False):
    """更新 uuid <-> filename 索引

    Args:
        uuid (_type_): _description_
        filename (str): _description_
        remove (bool, optional): 是否为删除操作. Defaults to False.
    """
    if remove:     # 删除
        uuid_to_file.pop(uuid)
        file_to_uuid.pop(filename)
    else:          # 新增
        uuid_to_file[uuid] = filename
        file_to_uuid[filename] = uuid


@model_bp.route('/list', methods=['GET'])
def fetch_model_list():
    """获取模型列表"""
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
    """获取指定模型的信息"""
    model_id = int(request.args['id'])
    # ? DEBUG
    print("choose model id: {}".format(model_id))
    # TODO 在 PaddleModel 中选中模型
    pass
    return jsonify({'code': -2, 'msg': 'not implement', 'data': None})


@model_bp.route('/fileUpload', methods=['POST'])
def upload_file():
    """上传文件"""
    file = request.files.get('file')
    if file is None:
        return jsonify({'code': -1, 'msg': 'failed', 'data': {}})
    # ? DEBUG
    print("filename: {}".format(file.filename))
    # 保存文件到缓存路径
    return_code, file_uuid, cache_file_path = f_utils.cache_file(file)
    file_columns = f_utils.get_file_columns(cache_file_path)
    preview_data = f_utils.preview_data(cache_file_path)
    merged_data = f_utils.preview_data(cache_file_path, full=True)
    # 重复文件，从 file_to_uuid 索引表中获取
    if return_code == 1:
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
        'merged': merged_data,
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
        # TODO 重复文件处理
        return jsonify({'code': 0, 'msg': 'duplicated file', 'data': response_data})
    else:
        return jsonify({'code': -1, 'msg': 'failed', 'data': {}})


@model_bp.route('/fileRemove', methods=['POST'])
def remove_file():
    file_id = request.args['id']
    # ? DEBUG
    file_name = uuid_to_file[file_id]
    file_path = os.path.join(cache_dir, file_name)
    # ? DEBUG
    print("====================")
    print("file_id: {}".format(file_id))
    print("file_name: {}".format(file_name))
    print("file_path: {}".format(file_path))
    print("====================")
    if session.get('set_uuid', 'unknown') == 'unknown':
        print(f'Error: dataset not found!')
        return jsonify({'code': 1, 'msg': 'failed', 'data': None})
    else:
        cur_dset = f_utils.get_dset(session['set_uuid'])
        if cur_dset is None:
            print("Dataset not found!")
        else:
            f_utils.remove_file_from_dset(file_path, cur_dset.data_path)
    # 从缓存路径中删除文件
    return_code = f_utils.remove_file(file_path)
    # TODO remove 后在 data 中传更新后的 merged 数据
    if return_code == 0:
        uuid_to_file.pop(file_id)
        file_to_uuid.pop(file_name)
        merged_path = os.listdir(cur_dset.data_path)
        print(f'merged_path: {merged_path}')
        merged_file = merged_path[0] if merged_path != [] else None
        merged_data = f_utils.preview_data(
            os.path.join(cur_dset.data_path, merged_file), full=True
        ) if merged_file is not None else None
        return jsonify({'code': 0, 'msg': 'success', 'data': {'merged': merged_data}})
    else:
        return jsonify({'code': 1, 'msg': 'failed', 'data': None})


@model_bp.route('/fileDownload')
def download_csv():
    # TODO 修改为唯一路径
    file_path = 'result.csv'
    return send_file(file_path, as_attachment=True)