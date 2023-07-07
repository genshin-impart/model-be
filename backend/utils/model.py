# -*- coding: utf-8 -*-
import os

from backend.models import PaddleModel


def get_all_models():
    models = PaddleModel.query.all()
    return models