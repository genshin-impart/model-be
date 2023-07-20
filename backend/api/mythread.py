# -*- coding: utf-8 -*-
import time
import json
import threading
import subprocess
import pandas as pd


def redirect_output_to_socketio(process, cur_sio, cur_sid, mode: str):
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
        # 清理缓存
        cur_sio.sleep(0.1)
    print('Over. Total messages: ', msg_count)
    # TODO 从路径读取返回值
    result = pd.read_csv(
        'result.csv',
        parse_dates=['DATATIME'],
        infer_datetime_format=True,
    )
    # ? DEBUG
    print(result.head())
    result['DATATIME'] = result['DATATIME'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S'))
    result_list = result.values.tolist()
    # TODO 运行完成，发送 done 事件
    done_payload = {'type': mode, 'data': result_list}
    # ? DEBUG
    print(result_list[:5])
    cur_sio.emit('done', done_payload, to=cur_sid)


def start_subprocess_with_output_redirection(cur_sio, cur_sid, mode: str, params: dict):
    """启动子进程并重定向输出

    Args:
        cur_sio (_type_): _description_
    """
    # 启动子进程
    if mode == 'apply':
        # TODO 填充参数
        print(json.dumps(params, indent=4))
        out_chunk_len = params['out_chunk_len']
        storage_path = params['storage_path']
        data_path = params['dset_data_path']
        # ? DEBUG
        process = subprocess.Popen(['pwd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        process = subprocess.Popen(
            ['python', './backend/sub_entry.py', 'apply',
             str(out_chunk_len), storage_path, data_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
    else:
        # TODO 填充参数
        process = subprocess.Popen(
            ['python', './sub_train.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )
    # 创建一个单独的线程来读取子进程的输出，以避免阻塞，并发送到 SocketIO
    t = threading.Thread(target=redirect_output_to_socketio, args=(process, cur_sio, cur_sid, mode))
    t.start()


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

    def __init__(self, cur_sio, name, mode: str, params: dict = {}):
        # name 同时也是 request.sid
        threading.Thread.__init__(self, name=name)
        self.sio = cur_sio
        self.params = params
        self.running = True
        self.mode = mode # 'train' or 'apply'

    def stop(self):
        self.running = False

    def run(self):
        # 启动子进程并转发日志输出
        start_subprocess_with_output_redirection(self.sio, self.name, self.mode, self.params)
