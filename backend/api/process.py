# -*- coding: utf-8 -*-
# TODO 这部分 API 移植到 core 中
import os
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def new_datafit(df: pd.DataFrame):
    df2 = df[['WINDSPEED', 'PREPOWER']]
    df2 = df2.dropna()
    jug1 = (df2['PREPOWER'] <= 0) & (df2['WINDSPEED'] > 0.5)
    jug1 = df2[jug1].index
    df2.drop(jug1, inplace=True)
    jug2 = (df2['WINDSPEED'] > 25)
    jug2 = df2[jug2].index
    df2.drop(jug2, inplace=True)
    jug3 = (df2['PREPOWER'] > 200000)
    jug3 = df2[jug3].index
    df2.drop(jug3, inplace=True)

    def sigmoid(x, L, x0, k, b):
        y = L / (1 + np.exp(-k * (x - x0))) + b
        return y

    p0 = [max(df2['PREPOWER']), np.median(df2['WINDSPEED']), 1, min(df2['PREPOWER'])]
    popt, _ = curve_fit(sigmoid, df2['WINDSPEED'], df2['PREPOWER'], p0, method='dogbox')

    # WINDSPEED--->PREPOWER
    def SP0PW0(x):
        return popt[0] / (1 + np.exp(-popt[2] * (x - popt[1]))) + popt[3]

    # * 补全缺失值
    mask_prepower_isnull = df['PREPOWER'].isnull()
    df.loc[mask_prepower_isnull, 'PREPOWER'] = SP0PW0(df.loc[mask_prepower_isnull, 'WINDSPEED'])
    mask_roundaws_isnull = df['ROUND(A.WS,1)'].isnull()
    df.loc[mask_roundaws_isnull, 'ROUND(A.WS,1)'] = df.loc[mask_roundaws_isnull, 'WINDSPEED']
    mask_roundapower_isnull = df['ROUND(A.POWER,0)'].isnull()
    df.loc[mask_roundapower_isnull, 'ROUND(A.POWER,0)'] = SP0PW0(df.loc[mask_roundapower_isnull, 'ROUND(A.WS,1)'])
    mask_yd15_isnull = df['YD15'].isnull()
    df.loc[mask_yd15_isnull, 'YD15'] = SP0PW0(df.loc[mask_yd15_isnull, 'ROUND(A.WS,1)'])
    # * 修正 PREPOWER
    mask_prepower_fix1 = (df['PREPOWER'] <= 0) & (df['WINDSPEED'] > 1)
    df.loc[mask_prepower_fix1, 'PREPOWER'] = SP0PW0(df.loc[mask_prepower_fix1, 'WINDSPEED'])
    mask_prepower_fix2 = np.abs(df['PREPOWER'] - SP0PW0(df['WINDSPEED'])) > 20000
    df.loc[mask_prepower_fix2, 'PREPOWER'] = SP0PW0(df.loc[mask_prepower_fix2, 'WINDSPEED'])
    # * 修正 ROUND(A.POWER,0)
    mask_roundapower_fix1 = (df['ROUND(A.POWER,0)'] <= 0) & (df['ROUND(A.WS,1)'] > 1)
    df.loc[mask_roundapower_fix1, 'ROUND(A.POWER,0)'] = SP0PW0(df.loc[mask_roundapower_fix1, 'ROUND(A.WS,1)'])
    mask_roundapower_fix2 = np.abs(df['ROUND(A.POWER,0)'] - SP0PW0(df['ROUND(A.WS,1)'])) > 20000
    df.loc[mask_roundapower_fix2, 'ROUND(A.POWER,0)'] = SP0PW0(df.loc[mask_roundapower_fix2, 'ROUND(A.WS,1)'])
    # * 修正 YD15
    mask_yd15_fix1 = (df['YD15'] <= 0) & (df['ROUND(A.WS,1)'] > 1)
    df.loc[mask_yd15_fix1, 'YD15'] = SP0PW0(df.loc[mask_yd15_fix1, 'ROUND(A.WS,1)'])
    mask_yd15_fix2 = np.abs(df['YD15'] - SP0PW0(df['ROUND(A.WS,1)'])) > 20000
    df.loc[mask_yd15_fix2, 'YD15'] = SP0PW0(df.loc[mask_yd15_fix2, 'ROUND(A.WS,1)'])
    df.reset_index(inplace=True)
    return df, popt


def new_preprocess(df: pd.DataFrame):
    # 数据预处理
    df = df[[
        'DATATIME', 'WINDSPEED', 'PREPOWER', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY', 'PRESSURE', 'ROUND(A.WS,1)',
        'ROUND(A.POWER,0)', 'YD15'
    ]]
    df.drop_duplicates(subset=['DATATIME'], keep='first', inplace=True)
    df.sort_values(by='DATATIME', ascending=True, inplace=True)
    # ----------------------------------------
    len = df.index.size
    if len >= 172:
        middle_size = len % 172
        middle_mask = df.head(middle_size).index
        df.drop(middle_mask, inplace=True)
    df.set_index('DATATIME', inplace=True)
    # 数据拟合
    df, popt = new_datafit(df)
    return df, popt


def new_feature_engineer(df: pd.DataFrame, window_size: int = 172):
    df['ROUND(A.WS,1)'] = df['ROUND(A.WS,1)'].shift(periods=window_size).astype(np.float)
    df['ROUND(A.POWER,0)'] = df['ROUND(A.POWER,0)'].shift(periods=window_size).astype(np.float)
    df['YD15'] = df['YD15'].shift(periods=window_size).astype(np.float)
    df.drop(df.head(window_size).index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def process_before_predict(df: pd.DataFrame):
    # 预处理
    df, popt = new_preprocess(df)
    # 特征工程
    df = new_feature_engineer(df)
    return df, popt


def new_output_control(res: pd.DataFrame, tail: pd.DataFrame, popt):

    def func(x):
        return popt[0] / (1 + np.exp(-popt[2] * (x - popt[1]))) + popt[3]

    def process_row(row):
        if not pd.isnull(row['PREPOWER']):
            if abs(row['YD15'] - row['PREPOWER']) > 10:
                row['YD15'] = row['PREPOWER']
            else:
                row['YD15'] = (row['YD15'] + row['PREPOWER']) / 2

            if abs(row['ROUND(A.POWER,0)'] - row['PREPOWER']) > 10:
                row['ROUND(A.POWER,0)'] = row['PREPOWER']
            else:
                row['ROUND(A.POWER,0)'] = (row['ROUND(A.POWER,0)'] + row['PREPOWER']) / 2
        elif not pd.isnull(row['WINDSPEED']):
            if abs(row['YD15'] - func(row['WINDSPEED'])) > 10:
                row['YD15'] = func(row(('WINDSPEED')))
            else:
                row['YD15'] = (row['YD15'] + func(row['WINDSPEED'])) / 2

            if abs(row['ROUND(A.POWER,0)'] - func(row['WINDSPEED'])) > 10:
                row['ROUND(A.POWER,0)'] = func(row['WINDSPEED'])
            else:
                row['ROUND(A.POWER,0)'] = (row['ROUND(A.POWER,0)'] + func(row['WINDSPEED'])) / 2

        row['YD15'] -= 3000
        if abs(row['YD15']) > 20000:
            row['YD15'] -= 2000
        if abs(row['YD15']) > 40000:
            row['YD15'] -= np.random.randint(1, 2000)
        return row

    res = res.apply(process_row, axis=1)
    return res