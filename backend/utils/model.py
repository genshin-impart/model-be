# -*- coding: utf-8 -*-
import os

from models import PaddleModel, DatasetInfo, BindingModel


def get_all_models():
    models = PaddleModel.query.all()
    return models


def get_paddle_model(model_id: int):
    model = PaddleModel.query.get(model_id)
    return model


def get_paddle_dset(set_id: int):
    paddle_dset = DatasetInfo.query.filter_by(uuid=set_id).first()
    return paddle_dset