# -*- coding: utf-8 -*-
import time
import json
import subprocess
import threading

from flask import request

import api.model as model_api
from extensions import my_socketio
from utils.model import get_paddle_model, get_paddle_dset

threads_dict = {}  # <k, v>: <thread name, thread object>


class ModelThread(threading.Thread):

    def __init__(self, cur_socketio, name, target=None):
        threading.Thread.__init__(self, name=name) # name 同时也是 request.sid
        self.socketio = cur_socketio
        self.target = target
        self.running = True
        self.result = None
        self.mode = None                           # 'train' or 'apply'

    def stop(self):
        self.running = False

    def run(self):
        # TODO 根据 self.mode 运行模型
        # 模拟发送日志
        for progress in range(100 + 1):
            time.sleep(0.1)
            # 发送进度
            self.socketio.emit('progress', progress / 100.0, to=self.name)
            if progress % 2 == 0:
                # 发送日志
                self.socketio.send('[Log] this is a log ...', to=self.name)
        # self.result = [[]] if self.target is None else self.target()
        # TODO 用真实数据填充，'train' 返回在整个数据集上的验证曲线值，'apply' 仅返回预测曲线值
        self.result = [
            ['2022-07-01 00:00:00', 6.0, 44224.0, 270, 3.9, 45, 842, 3.3, 17959.0, 13819.0],
            ['2022-07-01 00:15:00', 5.8, 43591.0, 274, 3.6, 46, 842, 3.9, 25930.0, 20435.0],
            ['2022-07-01 00:30:00', 5.7, 42842.0, 281, 3.3, 47, 842, 4.1, 31287.0, 25376.0],
            ['2022-07-01 00:45:00', 5.5, 42093.0, 289, 3.0, 48, 842, 4.3, 32626.0, 25669.0],
            ['2022-07-01 01:00:00', 5.4, 41344.0, 296, 2.7, 49, 842, 3.7, 24645.0, 24036.0]
        ]
        # TODO 运行完成，发送 done 事件
        done_payload = {
            'type': 'train',    # 'train' or 'apply', depending on frontend message
            'data': self.result
        }
        self.socketio.emit('done', done_payload, to=self.name)


class RealThread(threading.Thread):

    def __init__(self, cur_sio, name, mode: str = 'train', target=None, params: dict = {}):
        threading.Thread.__init__(self, name=name) # name 同时也是 request.sid
        self.sio = cur_sio
        self.target = target
        self.params = params
        self.running = True
        self.result = None
        self.mode = mode                           # 'train' or 'apply'

    def stop(self):
        self.running = False

    def run(self):
        result = self.target(self.params)
        done_payload = {'type': self.mode, 'data': result}
        self.sio.emit('done', done_payload, to=self.name)


def redirect_output_to_socketio(process, cur_sio, cur_sid):
    """重定向子进程输出到 SocketIO

    Args:
        process (_type_): _description_
        cur_sio (_type_): _description_
        cur_sid (_type_): _description_
    """
    msg_count = 0
    for line in process.stdout:
        cur_sio.emit('message', line.strip(), to=cur_sid)
        msg_count += 1
        cur_sio.sleep(0.1) # 清理缓存
    print('Over. Total messages: ', msg_count)
    # TODO 从路径读取返回值
    # cur_sio.emit('done', done_payload, to=cur_sid)
    cur_sio.send('done', to=cur_sid)


def start_subprocess_with_output_redirection(cur_sio, cur_sid, target):
    """启动子进程并重定向输出

    Args:
        cur_sio (_type_): _description_
    """
    # 启动子进程
    # TODO 分离 apply_model 和 train_model
    process = subprocess.Popen(
        ['python', ''], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
    )
    # 创建一个单独的线程来读取子进程的输出，以避免阻塞，并发送到 SocketIO
    t = threading.Thread(redirect_output_to_socketio, args=(process, cur_sio, cur_sid))
    t.start()


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
    target = model_api.train_model if mode == 'train' else model_api.apply_model
    t = RealThread(my_socketio, name=cur_socket_id, mode=mode, target=target, params=params)
    threads_dict[cur_socket_id] = t # 登记进程信息
    t.start()
    server_msg = '[Run] Model mission start.'
    my_socketio.send(server_msg, to=request.sid)


@my_socketio.on('retry')
def handle_retry():
    # TODO 更新出错，重新向服务端发送 retry 请求，负载是请求的文件，服务端按需重新运行或发送，直到成功
    pass