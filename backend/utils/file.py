# -*- coding: utf-8 -*-
import os
import shutil
import uuid

from backend.models import DatasetInfo
from backend.extensions import db

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
    if file.filename in cached_files: # 已经保存过
        return 1, ''
    try:
        file.save(os.path.join(cachedir, file.filename))
        file_uuid = uuid.uuid1()
    except IOError as e:
        return -1, ''
    return 0, file_uuid


def remove_file(file):
    """ 删除缓存的文件 """


def concat_files(filename_list: list):
    """ 将上传的一个或多个文件组装成一组数据 """
    cached_files = os.listdir(cachedir)
    dset_path = os.path.join(datadir, uuid.uuid4().hex)
    if not os.path.exists(dset_path):
        os.mkdir(dset_path)
    for filename in filename_list:
        if filename not in cached_files:
            raise "File not exists!"
        # 移动文件 f_src --> f_dst (cache/filename.csv --> data/<random_numbers:32>/filename.csv)
        f_src = os.path.join(cachedir, filename)
        f_dst = os.path.join(dset_path, filename)
        shutil.move(f_src, f_dst)
    # 创建数据集
    create_dset(dset_path)


def create_dset(dset_path: str):
    """ 创建新数据集 """
    paddle_dset = DatasetInfo(data_path=dset_path)
    if not paddle_dset.validate_files():
        raise "Invalid file format!"
    db.session.add(paddle_dset)
    db.session.commit()


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
