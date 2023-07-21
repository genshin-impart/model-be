# -*- coding: utf-8 -*-

# ==================== modules ====================
# * Standard modules
import os
import json
import random
import string
import datetime
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

from api.process import process_before_predict, new_output_control
from api.train import generate_model

# * Core modules
from core.modules.new_model import create_model


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


def apply_model(out_chunk_len: int, storage_path: str, data_path: str, output_control: bool = False):
    """运行模型。可以作为子进程启动。"""
    # TODO 合并数据集，在 DatasetInfo 中操作
    if not os.path.exists(data_path):
        raise "invalid data path!"
    merge_datafiles_dir(data_path)
    # 读取数据集
    test_df = pd.read_csv(
        os.path.join(data_path,
                     os.listdir(data_path)[0]),
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
    tail_mask = test_df.tail(out_chunk_len)
    # TODO 修改为 in_chunk_len
    test_df, popt = process_before_predict(test_df, out_chunk_len)
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
    loaded_model0 = load(os.path.join(storage_path, 'paddlets-ensemble-model0'))
    loaded_model1 = load(os.path.join(storage_path, 'paddlets-ensemble-model1'))
    res0 = scaler.inverse_transform(loaded_model0.predict(test_dataset_scaled))
    res1 = scaler.inverse_transform(loaded_model1.predict(test_dataset_scaled))
    result = res0.to_dataframe() * 0.5 + res1.to_dataframe() * 0.5
    # 输出控制
    if output_control:
        result = new_output_control(result, tail_mask, popt)
    result.reset_index(inplace=True)
    result.rename(columns={"index": "DATATIME"}, inplace=True)
    print('==================== result ====================')
    result = result[['DATATIME', 'ROUND(A.POWER,0)', 'YD15']]
    # TODO 保存到文件
    result.to_csv('result.csv', index=False)
    result['DATATIME'] = result['DATATIME'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d %H:%M:%S'))
    result_list = result.values.tolist()
    # ? DEBUG
    print(f'预测时间长度: {len(result_list)}')
    print(f'预测时间范围: {result_list[0][0]} ~ {result_list[-1][0]}')
    return result_list


# TODO 修改参数列表
def train_model(
    data_path: str, storage_path: str, name: str, description: str, in_chunk_len: int, out_chunk_len: int,
    learning_rate: float, batch_size: int, epochs: int
):
    # TODO 训练模型
    data_path = os.path.join(data_path, os.listdir(data_path)[0])
    params = {
        'inWindowSize': in_chunk_len,
        'outWindowSize': out_chunk_len,
        'learningRate': learning_rate,
        'batchSize': batch_size,
        'epochs': epochs
    }
    new_paddle_model = generate_model(data_path, params)
    print('new model will be saved to: ', storage_path)
    new_paddle_model.save(storage_path)
    # ? DEBUG
    print('new model has been saved to: ', storage_path)
    print('模型训练完毕！')
    # TODO 返回验证集上的结果
    return [[]]


def realtime_predict(
    storage_path: str, csv_path: str, in_chunk_len: int, out_chunk_len: int, output_control: bool = False
):
    """滚动预测。可以作为子进程启动。"""
    # 读取数据集
    test_df = pd.read_csv(
        csv_path,
        parse_dates=['DATATIME'],
        infer_datetime_format=True,
        dayfirst=True,
        dtype={
            'WINDDIRECTION': np.float,
            'HUMIDITY': np.float,
            'PRESSURE': np.float,
        }
    )
    # 预处理
    test_df.drop_duplicates(subset=['DATATIME'], keep='first', inplace=True)
    print(f'len of test_df: {len(test_df)}')
    print(test_df)
    if len(test_df) < in_chunk_len:
        return False
    # TODO 使用 out_chunk_len
    tail_mask = test_df.tail(out_chunk_len)
    # TODO 修改为 in_chunk_len
    test_df, popt = process_before_predict(test_df, out_chunk_len)
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
    loaded_model0 = load(os.path.join(storage_path, 'paddlets-ensemble-model0'))
    loaded_model1 = load(os.path.join(storage_path, 'paddlets-ensemble-model1'))
    res0 = scaler.inverse_transform(loaded_model0.predict(test_dataset_scaled))
    res1 = scaler.inverse_transform(loaded_model1.predict(test_dataset_scaled))
    result = res0.to_dataframe() * 0.5 + res1.to_dataframe() * 0.5
    # 输出控制
    if output_control:
        result = new_output_control(result, tail_mask, popt)
    result.reset_index(inplace=True)
    result.rename(columns={"index": "DATATIME"}, inplace=True)
    print('==================== result ====================')
    result = result[['DATATIME', 'ROUND(A.POWER,0)', 'YD15']]
    res_path = os.path.join(os.path.dirname(csv_path), 'res.csv')
    result.to_csv(res_path, index=False)
    return True