# -*- coding: utf-8 -*-
from models import PaddleModel, DatasetInfo


def get_all_models():
    """获取所有模型

    Returns:
        _type_: 所有模型
    """
    models = PaddleModel.query.all()
    return models


def get_paddle_model(model_id: int):
    """获取指定模型

    Args:
        model_id (int): 模型 id

    Returns:
        _type_: 指定的模型对象
    """
    model = PaddleModel.query.get(model_id)
    return model


def get_paddle_dset(set_id: int):
    """获取指定数据集

    Args:
        set_id (int): 数据集 id

    Returns:
        _type_: 指定的数据集对象
    """
    paddle_dset = DatasetInfo.query.filter_by(uuid=set_id).first()
    return paddle_dset