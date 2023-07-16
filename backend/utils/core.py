# -*- coding: utf-8 -*-
import os

from models import DatasetInfo
from extensions import db

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
coredir = os.path.join(basedir, 'model-core')


def create_and_train_model(set_id: str, model_config_dict: dict):
    # TODO 查找数据集表，定位数据集
    target_dataset = DatasetInfo.query.first()
    if target_dataset is None:
        pass
    data_dir = str(target_dataset.data_path)
    if os.path.exists(data_dir):
        pass
    pass


if __name__ == '__main__':
    print("coredir: ", coredir)