# -*- coding: utf-8 -*-

# ==================== modules ====================
# * Standard modules
import os
import random
import string
import threading
import subprocess
import numpy as np
import pandas as pd

# * Paddle modules
from paddlets import TSDataset
from paddlets.models.model_loader import load
from paddlets.transform import StandardScaler

# * Project modules
from models import DatasetInfo, PaddleModel, BindingModel
from extensions import db, my_socketio
from utils.model import get_paddle_model, get_paddle_dset
from utils.data_process import merge_datafiles_dir

from process import process_before_predict, new_output_control
from train import generate_model

# * Core modules
from core.modules.new_model import create_model

# ==================== configs ====================
# * Directory configs
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
coredir = os.path.join(basedir, 'core')
modeldir = os.path.join(coredir, 'model')


def random_str(rand_len: int = 8):
    """生成随机定长字符串

    Args:
        rand_len (int, optional): 随机字符串长度. Defaults to 8.

    Returns:
        str: 随机生成的定长字符串
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=rand_len))


class MyThread(threading.Thread):

    def __init__(self, cur_sio, name, target=None):
        threading.Thread.__init__(self)
        self.sio = cur_sio
        self.target = target
        self.running = True
        self.result = None

    def stop(self):
        self.running = False

    def run(self):
        # TODO
        self.result = [[]] if self.target is None else self.target()
        self.sio.emit('Done', self.result)


def apply_model(model_id: int, set_id: int, output_control: bool = False):
    """运行模型。可以作为子进程启动。

    Args:
        model_id (int): 模型 id
        set_id (int): 数据集 id
    """
    model = get_paddle_model(model_id)
    if model is None:
        print(f'Error: model {model_id} not found!')
        return None
    dset = get_paddle_dset(set_id)
    if dset is None:
        print(f'Error: set with uuid {set_id} not found!')
        return None
    # TODO 合并数据集，在 DatasetInfo 中操作
    merge_datafiles_dir(dset.data_path)
    # 读取数据集
    test_df = pd.read_csv(
        os.path.join(dset.data_path,
                     os.listdir(dset.data_path)[0]),
        parse_dates=['DATATIME'],
        infer_datetime_format=True,
        dayfirst=True,
        dtype={
            'WINDDIRECTION': np.float,
            'HUMIDITY': np.float,
            'PRESSURE': np.float,
        }
    )
    # TODO 预处理
    test_df.drop_duplicates(subset=['DATATIME'], keep='first', inplace=True)
    # TODO 使用 out_chunk_len
    tail_mask = test_df.tail()
    test_df, popt = process_before_predict(test_df)
    # 构造测试集
    test_dataset = TSDataset.load_from_dataframe(
        test_df,
        time_col='DATATIME',
        target_cols=['ROUND(A.WS,1)', 'ROUND(A.POWER,0)', 'YD15'],
        observed_cov_cols=['WINDSPEED', 'PREPOWER', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY', 'PRESSURE'],
        freq='15min',
        fill_missing_dates=True,
        fillna_method='pre'
    )
    # 归一化
    scaler = StandardScaler()
    scaler.fit(test_dataset)
    test_dataset_scaled = scaler.transform(test_dataset)
    # * 加载模型，默认使用集成模型
    loaded_model0 = load(os.path.join(model.storage_path, 'paddlets-ensemble-model0'))
    loaded_model1 = load(os.path.join(model.storage_path, 'paddlets-ensemble-model1'))
    res0 = scaler.inverse_transform(loaded_model0.predict(test_dataset_scaled))
    res1 = scaler.inverse_transform(loaded_model1.predict(test_dataset_scaled))
    result = res0.to_dataframe() * 0.5 + res1.to_dataframe()
    # 输出控制
    if output_control:
        result = new_output_control(result, tail_mask, popt)
    result.reset_index(inplace=True)
    result = result[['DATATIME', 'ROUND(A.POWER,0)', 'YD15']]
    return result


def train_model(set_id: int, params: dict):
    dset = get_paddle_dset(set_id)
    if dset is None:
        print(f'Error: set with uuid {set_id} not found!')
        return None
    # 创建模型并训练
    new_model = PaddleModel(
        name=params['name'],
        description=params['description'],
        in_chunk_len=params['inWindowSize'],
        out_chunk_len=params['outWindowSize'],
        learning_rate=params['learningRate'],
        batch_size=params['batchSize'],
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
    new_model.storage_path = os.path.join(modeldir, storage_path)
    new_model.update()
    # TODO 训练模型
    data_path = os.path.join(dset.data_path, os.listdir(dset.data_path)[0])
    new_paddle_model = generate_model(data_path, params)
    new_paddle_model.save(new_model.storage_path)


def handle_model_params(params_dict: dict):
    """解析模型参数

    Args:
        params_dict (dict): 参数字典. e.g. {'task': 'apply', 'modelId': 1, 'setId': "35059859-8046-4e85-b36a-5cde76480405"} or
                                     {'task': 'train', 'setId': "35059859-8046-4e85-b36a-5cde76480405", 'params': {
                                         'inWindowSize': 100,
                                         'outWindowSize': 10,
                                         'epochs': 20,
                                         'batchSize': 32,
                                         'learningRate': 0.001,
                                     }}
    """
    if params_dict['task'] == 'apply':
        # 运行模型
        return apply_model(params_dict['modelId'], params_dict['setId'])
    elif params_dict['task'] == 'train':
        # 训练模型
        return train_model(params_dict['setId'], params_dict['params'])
    else:
        print("Invalid task type!")