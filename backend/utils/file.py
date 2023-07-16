# -*- coding: utf-8 -*-
import os
import shutil
import uuid

import pandas as pd

from models import DatasetInfo
from extensions import db

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
cachedir = os.path.join(basedir, 'cache')
datadir = os.path.join(basedir, 'data')


def cache_file(file):
    """ 缓存上传的文件 """
    if not os.path.exists(cachedir):
        os.mkdir(cachedir)
    # TODO 清理长时间未使用的文件
    pass
    # TODO 查找文件
    cached_files = os.listdir(cachedir)
    cache_file_path = os.path.join(cachedir, file.filename)
    if file.filename in cached_files: # 已经保存过
        return 1, '', cache_file_path
    try:
        file.save(cache_file_path)
        file_uuid = uuid.uuid1().hex
    except IOError as e:
        print(str(e))
        return -1, '', ''
    return 0, file_uuid, cache_file_path


def remove_file(file_path: str):
    """ 删除缓存的文件 """
    try:
        os.remove(file_path)
    except Exception as e:
        print(str(e))
        return 1
    return 0


def merge_file_to_dset(cache_file_path: str, dset_data_path: str):
    # TODO 增加 col 校验
    if not os.path.exists(cache_file_path):
        print("File not exists!")
        return False
    filename = os.path.basename(cache_file_path)
    try:
        # shutil.move(cache_file_path, os.path.join(dset_data_path, filename))
        shutil.copy(cache_file_path, os.path.join(dset_data_path, filename))
    except IOError as e:
        print(str(e))
        return False
    return True


def create_dset():
    """ 创建新数据集 """
    paddle_dset = DatasetInfo()
    db.session.add(paddle_dset)
    db.session.commit()
    return paddle_dset


def get_dset(set_uuid):
    """ 查找数据集 (set_uuid) """
    if set_uuid is None:
        return None
    paddle_dset = DatasetInfo.query.filter_by(uuid=set_uuid).first()
    return paddle_dset


def delete_dset(dset_path: str):
    """ 删除数据集 """
    paddle_dset = DatasetInfo.query.filter_by(data_path=dset_path).first()

    if paddle_dset is None:
        raise "Invalid dataset id!"
    if paddle_dset.use_count != 0:
        # TODO 删除数据集会对现有的绑定模型有影响，给出 warning
        pass

    dset_path = str(paddle_dset.data_path)
    shutil.rmtree(dset_path)
    db.session.delete(paddle_dset)
    db.session.commit()


def delete_dset_byid(dset_id: int):
    """ 删除数据集 (id) """
    paddle_dset = DatasetInfo.get(dset_id)

    if paddle_dset is None:
        raise "Invalid dataset id!"
    if paddle_dset.use_count != 0:
        # TODO 删除数据集会对现有的绑定模型有影响，给出 warning
        pass

    dset_path = str(paddle_dset.data_path)
    shutil.rmtree(dset_path)
    db.session.delete(paddle_dset)
    db.session.commit()


def preview_data(file_path: str, full: bool = False):
    df = pd.read_csv(file_path)
    df_list = df.values.tolist()
    # TODO 如果是全部数据则对 NaN 进行处理
    return df_list[:100] if full else df_list[:5] # 预览前 5 行


def get_file_columns(cache_file_path: str):
    if cache_file_path == '':
        return []
    df = pd.read_csv(cache_file_path)
    return list(df.columns)