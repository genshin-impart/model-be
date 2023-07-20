# -*- coding: utf-8 -*-
import time
import json
import subprocess
import threading

from flask import request

import api.model as model_api
from extensions import my_socketio
from utils.model import get_paddle_model, get_paddle_dset
from api.mythread import RealThread, ModelThread

threads_dict = {}  # <k, v>: <thread name, thread object>


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
    # TODO 资源释放，thread
    server_msg = '[Server] Client disconnected.'
    my_socketio.send(server_msg, to=request.sid)


@my_socketio.on('run')
def handle_run(data):
    cur_socket_id = str(request.sid)
    # TODO 解析参数
    mode = data['task']             # 'train' or 'apply'
    params = {}
    paddle_dset = get_paddle_dset(data['setId'])
    if mode == 'apply':
        paddle_model = get_paddle_model(data['modelId'])
        params['out_chunk_len'] = paddle_model.out_chunk_len
        params['storage_path'] = paddle_model.storage_path
        params['dset_data_path'] = paddle_dset.data_path
    elif mode == 'train':
        pass
    else:
        print(f'Error: unsupported task type {mode}!')
                                    # target = model_api.train_model if mode == 'train' else model_api.apply_model
                                    # t = RealThread(my_socketio, name=cur_socket_id, mode=mode, target=target, params=params)
    t = RealThread(my_socketio, name=cur_socket_id, mode=mode, params=params)
    threads_dict[cur_socket_id] = t # 登记进程信息
    t.start()
    server_msg = '[Run] Model mission start.'
    my_socketio.send(server_msg, to=request.sid)


@my_socketio.on('retry')
def handle_retry():
    # TODO 更新出错，重新向服务端发送 retry 请求，负载是请求的文件，服务端按需重新运行或发送，直到成功
    pass