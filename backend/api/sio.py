# -*- coding: utf-8 -*-
import os
import shutil
import time
import json
import random
import string
import subprocess
import threading
import pandas as pd

from flask import request

import api.model as model_api
from models import PaddleModel
from extensions import my_socketio
from utils.model import get_paddle_model, get_paddle_dset
from api.mythread import RealThread, ModelThread

threads_dict = {}  # <k, v>: <thread name, thread object>
csv_dict = {}      # <k, v>: <threadnaem, csv data path>

# * Directory configs
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
coredir = os.path.join(basedir, 'core')
modeldir = os.path.join(coredir, 'model')
csvdir = os.path.join(basedir, 'csv')


def random_str(rand_len: int = 8):
    """生成随机定长字符串

    Args:
        rand_len (int, optional): 随机字符串长度. Defaults to 8.

    Returns:
        str: 随机生成的定长字符串
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=rand_len))


def append_list_to_csv(data_list: list, csv_path: str):
    """将列表追加到 csv 文件中

    Args:
        data_list (list): 待追加的数据列表
        csv_path (str): csv 文件路径
    """
    # 将数据列表转换为 DataFrame
    df = pd.DataFrame(data_list[1:], columns=data_list[0])
    # 将 DataFrame 追加到 csv 文件中
    if not os.path.exists(csv_path):
        print(f'[Server] {csv_path} does not exist, creating ...')
        df.to_csv(csv_path, index=False)
    else:
        print(f'[Server] {csv_path} exists, appending ...')
        df.to_csv(csv_path, mode='a', index=False, header=False)


@my_socketio.on('connect')
def handle_connect():
    print('[Server] SocketIO connection established.')
    # 创建 thread
    cur_socket_id = str(request.sid)
    # t = ModelThread(my_socketio, name=cur_socket_id)
    # t = RealThread(my_socketio, name=cur_socket_id)
    # threads_dict[cur_socket_id] = t
    # ? DEBUG
    print('cur_socket_id: ', cur_socket_id)
    server_msg = '[Server] Client connected.'
    my_socketio.send(server_msg, to=request.sid)


@my_socketio.on('disconnect')
def handle_disconnect():
    cur_socket_id = str(request.sid)
    t = threads_dict[cur_socket_id]
    t.stop()
    threads_dict.pop(cur_socket_id)
    # TODO 资源释放
    if cur_socket_id in csv_dict.keys():
        csv_data_path = csv_dict[cur_socket_id]
        shutil.rmtree(os.path.join(csvdir, csv_data_path))
        shutil.rmtree(os.path.join(os.path.dirname(csv_data_path), 'res.csv'))
        csv_dict.pop(cur_socket_id)
    server_msg = '[Server] Client disconnected.'
    my_socketio.send(server_msg, to=request.sid)


@my_socketio.on('run')
def handle_run(data):
    cur_socket_id = str(request.sid)
    # ? DEBUG
    print('====================')
    print(json.dumps(data, indent=4))
    # TODO 解析参数
    mode = data['task']
    params = {}
    # * 应用模型
    if mode == 'apply':
        paddle_dset = get_paddle_dset(data['setId'])
        if paddle_dset is None:
            print(f'Error: dataset {data["setId"]} not found!')
        # 设置 apply 参数
        paddle_model = get_paddle_model(data['modelId'])
        params = {
            'out_chunk_len': paddle_model.out_chunk_len,
            'storage_path': paddle_model.storage_path,
            'dset_data_path': paddle_dset.data_path
        }
    # * 训练模型
    elif mode == 'train':
        paddle_dset = get_paddle_dset(data['setId'])
        if paddle_dset is None:
            print(f'Error: dataset {data["setId"]} not found!')
        model_params = data['modelParams']
        # 设置 train 参数
        params = {
            'name': model_params['name'],
            'description': model_params.get('description', model_params['name']),
            'in_chunk_len': model_params['inWindowSize'],
            'out_chunk_len': model_params['outWindowSize'],
            'epochs': model_params['epoch'],
            'batch_size': model_params['batchSize'],
            'learning_rate': model_params['learningRate'],
            'dset_data_path': paddle_dset.data_path
        }
        # 创建模型对象
        new_model = PaddleModel(
            name=params['name'],
            description=params['description'],
            in_chunk_len=params['in_chunk_len'],
            out_chunk_len=params['out_chunk_len'],
            learning_rate=params['learning_rate'],
            batch_size=params['batch_size'],
        )
        try:
            new_model.update()
        except Exception as e:
            print(f"Error: create new model {params['name']} failed!")
            print(str(e))
            return None
        # 配置存储路径
        storage_path = random_str()
        while storage_path in os.listdir(modeldir):
            storage_path = random_str()
        model_storage_path = os.path.join(modeldir, storage_path)
        new_model.storage_path = model_storage_path
        new_model.update()
        params['model_storage_path'] = model_storage_path
    # * 滚动预测
    elif mode == 'realtime':
        # TODO 滚动预测模块
        paddle_model = get_paddle_model(data['modelId'])
        params = {
            'storage_path': paddle_model.storage_path,
            'in_chunk_len': paddle_model.in_chunk_len,
            'out_chunk_len': paddle_model.out_chunk_len,
        }
        print('========== csv_dict ==========')
        print(json.dumps(csv_dict, indent=4))
        # TODO 构造临时 csv 文件路径
        if not (cur_socket_id in csv_dict.keys()):
            csv_path = random_str()
            while csv_path in os.listdir(csvdir):
                csv_path = random_str()
            if not os.path.exists(os.path.join(csvdir, csv_path)):
                os.mkdir(os.path.join(csvdir, csv_path))
            csv_dict[cur_socket_id] = csv_path
        else:
            csv_path = csv_dict[cur_socket_id]
        tmp_csv_path = os.path.join(csvdir, csv_path, 'tmp.csv')
        tmp_data_list = [
            data['columns'],
            data['data'],
        ]
        # TODO 将接受到的数据写入临时 csv 文件
        append_list_to_csv(tmp_data_list, tmp_csv_path)
        params['csv_path'] = tmp_csv_path
    else:
        print(f'Error: unsupported task type {mode}!')
    t = RealThread(my_socketio, name=cur_socket_id, mode=mode, params=params)
    threads_dict[cur_socket_id] = t # 登记进程信息
    t.start()
    server_msg = '[Run] Model mission start.'
    my_socketio.send(server_msg, to=request.sid)


@my_socketio.on('retry')
def handle_retry():
    # TODO 更新出错，重新向服务端发送 retry 请求，负载是请求的文件，服务端按需重新运行或发送，直到成功
    pass