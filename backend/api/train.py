# -*- coding: utf-8 -*-
# * Base modules
import os
import numpy as np
import pandas as pd

# * Paddle modules
from paddlets import TSDataset
from paddlets.transform import StandardScaler

# * Project modules
from core.utils.my_configs import set_device, set_random_seed
from core.modules.new_model import create_model
from api.process import new_preprocess


def get_dset(data_path: str):
    df = pd.read_csv(
        data_path,
        parse_dates=['DATATIME'],
        infer_datetime_format=True,
        dayfirst=True,
        dtype={
            'WINDDIRECTION': np.float,
            'HUMIDITY': np.float,
            'PRESSURE': np.float,
        }
    )
    df['ROUND(A.WS,1)'] = df['ROUND(A.WS,1)'].replace(r'^\s*$', np.nan, regex=True)
    df[['ROUND(A.WS,1)']] = df[['ROUND(A.WS,1)']].astype(np.float)
    return df


def generate_model(data_path: str, params: dict, window_size: int = 172):
    set_device()
    set_random_seed()
    df = get_dset(data_path)
    # 预处理
    df, _ = new_preprocess(df)
    # 移位
    df['ROUND(A.WS,1)'] = df['ROUND(A.WS,1)'].shift(window_size).astype(np.float)
    df['ROUND(A.POWER,0)'] = df['ROUND(A.POWER,0)'].shift(window_size).astype(np.float)
    df['YD15'] = df['YD15'].shift(window_size).astype(np.float)
    df['DATATIME'] = df['DATATIME'].shift(window_size)
    df.drop(df.head(window_size).index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # 数据集构造
    target_cov_dataset = TSDataset.load_from_dataframe(
        df,
        time_col='DATATIME',
        target_cols=['ROUND(A.WS,1)', 'ROUND(A.POWER,0)', 'YD15'],
        observed_cov_cols=['WINDSPEED', 'PREPOWER', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY', 'PRESSURE'],
        freq='15min',
        fill_missing_dates=True,
        fillna_method='pre'
    )
    # 划分数据集
    train_dataset, val_dataset = target_cov_dataset.split(0.8)
    # 归一化
    scaler = StandardScaler()
    scaler.fit(train_dataset)
    train_dataset_scaled, val_dataset_scaled = scaler.transform(train_dataset), scaler.transform(val_dataset)
    # 训练模型
    new_model = create_model(
        in_chunk_len=params['inWindowSize'],
        out_chunk_len=params['outWindowSize'],
        batch_size=params['batchSize'],
        max_epochs=params['epochs'],
        learning_rate=params['learningRate']
    )
    new_model.fit(train_dataset_scaled, val_dataset_scaled)
    return new_model