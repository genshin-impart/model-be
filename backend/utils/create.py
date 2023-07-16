# -*- coding: utf-8 -*-
import os

from models import PaddleModel, BindingModel, DatasetInfo
from extensions import db


def get_model(model_id: int):
    model = PaddleModel.get(model_id)
    return model


def create_binding(task_params):
    """创建一个运行任务
    """
    # TODO 解析传入的参数
    # * apply mode
    pass
    # * train mode
    pass