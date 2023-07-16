# -*- coding: utf-8 -*-

# ==================== modules ====================
# * Standard modules
import os
import threading
import subprocess

# * Project modules
from models import DatasetInfo, PaddleModel, BindingModel
from extensions import db

# * Core modules
from core.modules.new_model import create_model

# ==================== configs ====================
# * Directory configs
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
coredir = os.path.join(basedir, 'core')


class MyThread(threading.Thread):

    def __init__(self, cur_sio, name, target=None):
        threading.Thread.__init__(self)
        self.sio = cur_sio
        self.target = target
        self.running = True
        self.result = None

    def stop(self):
        self.running = False

    def run(self):
        # TODO
        self.result = [[]] if self.target is None else self.target()
        self.sio.emit('Done', self.result)