# -*- coding: utf-8 -*-
import os

from models import PaddleModel, DatasetInfo, BindingModel


def get_all_models():
    models = PaddleModel.query.all()
    return models