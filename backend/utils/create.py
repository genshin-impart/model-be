# -*- coding: utf-8 -*-
import os

from backend.models import PaddleModel, BindingModel
from backend.extensions import db


def get_model(model_id: int):
    model = PaddleModel.get(model_id)
    return model


def create_binding(model_id: int, file_path: str):
    pass