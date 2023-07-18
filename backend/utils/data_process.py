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


def merge_datafiles_dir(data_dir: str):
    files = os.listdir(data_dir)
    if len(files) == 1:
        # 只有一个文件，直接返回
        return
    # TODO 合并文件
    for f in files:
        data_file = os.path.join(data_dir, f)
        # 获取文件名前缀
        data_basename = os.path.basename(data_file)
        # 检查风机数据是否有多个数据文件. e.g. 4-1.csv, 4-2.csv, ...
        if len(data_basename.split('-')) > 1:
            merge_list = []
            # 找出该风机的所有数据文件
            f_matches = [_f for _f in files if (_f.find(data_basename.split('-')[0] + '-') > -1)]
            for f_match in f_matches:
                # 读取该部分数据
                data_df = pd.read_csv(os.path.join(data_dir, f_match), index_col=False, keep_default_na=False)
                merge_list.append(data_df)
            if len(merge_list) > 0:
                all_data = pd.concat(merge_list, axis=0, ignore_index=True).fillna(".")
                all_data.to_csv(os.path.join(data_dir, data_basename.split('-')[0] + '.csv'), index=False)
                # ? DEBUG
                print('====================')
                print('merged files: ', f_matches)
                print('====================')
            for f_match in f_matches:
                # 删除这部分数据文件
                os.remove(os.path.join(data_dir, f_match))


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
