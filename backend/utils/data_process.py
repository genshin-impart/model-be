# -*- coding: utf-8 -*-
import os
import pandas as pd


def transfer_datafiles(data_dir: str):
    """ 将 xlsx、xls 等文件转换为 csv 文件 """
    if not os.path.isdir(data_dir):
        raise "Invalid data path!"
    files = os.listdir(data_dir)
    for f in files:
        data_path = os.path.join(data_dir, f)
        data_name, data_type = os.path.splitext(data_path)
        if data_type == 'xlsx':
            data_xls = pd.read_excel(data_path, index_col=0, na_values='')
            data_xls.to_csv(data_name + '.csv', encoding='utf-8')
            # os.remove(data_path) # 删除源文件


def validate_data(data: pd.DataFrame, data_cols=None):
    """ 校验 csv 文件的 col 是否一致，一致返回 0，仅顺序不一致返回 1，否则返回 2"""
    cur_cols = data.columns.tolist()
    if data_cols is None:
        data_cols = cur_cols.copy()
        return 0
    if cur_cols == data_cols:
        return 0
    elif set(cur_cols) == set(data_cols):
        return 1
    else:
        return 2
