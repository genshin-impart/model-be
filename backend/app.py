# -*- coding: utf-8 -*-
import os
import click
import time
import asyncio
import threading
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

import eventlet
from flask import Flask, request
from flask_socketio import SocketIO

from blueprints.user import user_bp
from blueprints.model import model_bp
from models import Admin, User, PaddleModel, BindingModel
from extensions import db, sess, cors
from settings import configs

basedir = os.path.abspath(os.path.dirname(__file__))

my_socketio = SocketIO()


def create_app(config_name=None):
    """ 创建 FLASK APP """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('wpf_system')
    app.config.from_object(configs[config_name])

    register_logging(app)    # config logging
    register_extensions(app) # config extensions, e.g. db
    register_blueprints(app) # config blueprints
    register_commands(app)   # config commands

    return app


def register_logging(app: Flask):
    """ 日志模块 """

    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not os.path.exists(os.path.join(basedir, 'logs')):
        os.mkdir(os.path.join(basedir, 'logs'))
    file_handler = RotatingFileHandler(
        os.path.join(basedir, 'logs/wpf_system.log'), maxBytes=10 * 1024 * 1024, backupCount=10
    )
    # file_handler.setFormatter(formatter)
    file_handler.setFormatter(request_formatter)
    file_handler.setLevel(logging.INFO)

    # if not app.debug:
    #     app.logger.addHandler(file_handler)
    app.logger.addHandler(file_handler)


def register_commands(app: Flask):
    """ 命令模块 """

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initializa the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='THe username used to login')
    @click.option(
        '--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login'
    )
    def init(username, password):
        """Building project just for you."""
        click.echo('Initializing the database ...')
        db.create_all()

        admin = Admin().query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating ...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account ...')
            admin = Admin(username=username)
            admin.set_password(password)
            db.session.add(admin)

        paddle_model = PaddleModel.query.first()
        if paddle_model is None:
            click.echo('Creating the default Paddle model ...')
            paddle_model = PaddleModel(
                description='Test default Paddle model',
                in_chunk_len=32,
                out_chunk_len=32,
                batch_size=32,
                learning_rate=0.001
            )
            db.session.add(paddle_model)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--user', default=3, help='Quantity of users, default is 3.')
    @click.option('--model', default=2, help='Quantity of models, default is 2.')
    @click.option('--bindings', default=0, help='Quantity of bindings, default is 0.')
    def forge(user, model, bindings):
        """Generate fake data."""
        from backend.fakes import fake_admin, fake_users, fake_models, fake_bindings

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator ...')
        fake_admin()

        click.echo('Generating %d users ...' % user)
        fake_users()

        click.echo('Generating %d models ...' % model)
        fake_models()

        click.echo('Generating %d bindings ...' % bindings)
        fake_bindings()

        click.echo('Done.')


def register_extensions(app: Flask):
    """ 扩展模块 """
    db.init_app(app)   # init database
    sess.init_app(app) # init session
    cors.init_app(app) # init cors


def register_blueprints(app: Flask):
    """ 蓝本模块 """
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(model_bp, url_prefix='/model')


threads_dict = {}  # <k, v>: <thread name, thread object>


class ModelThread(threading.Thread):

    def __init__(self, cur_socketio, name, target=None):
        threading.Thread.__init__(self, name=name) # name 同时也是 request.sid
        self.socketio = cur_socketio
        self.target = target
        self.running = True
        self.result = None
        self.mode = None                           # 'train' or 'apply'

    def stop(self):
        self.running = False

    def run(self):
        # TODO 根据 self.mode 运行模型
        # 模拟发送日志
        for progress in range(100 + 1):
            time.sleep(0.1)
            # 发送进度
            self.socketio.emit('progress', progress / 100.0, to=self.name)
            if progress % 2 == 0:
                # 发送日志
                self.socketio.send('[Log] this is a log ...', to=self.name)
        # self.result = [[]] if self.target is None else self.target()
        # TODO 用真实数据填充，'train' 返回在整个数据集上的验证曲线值，'apply' 仅返回预测曲线值
        self.result = [
            ['2022-07-01 00:00:00', 6.0, 44224.0, 270, 3.9, 45, 842, 3.3, 17959.0, 13819.0],
            ['2022-07-01 00:15:00', 5.8, 43591.0, 274, 3.6, 46, 842, 3.9, 25930.0, 20435.0],
            ['2022-07-01 00:30:00', 5.7, 42842.0, 281, 3.3, 47, 842, 4.1, 31287.0, 25376.0],
            ['2022-07-01 00:45:00', 5.5, 42093.0, 289, 3.0, 48, 842, 4.3, 32626.0, 25669.0],
            ['2022-07-01 01:00:00', 5.4, 41344.0, 296, 2.7, 49, 842, 3.7, 24645.0, 24036.0]
        ]
        # TODO 运行完成，发送 done 事件
        done_payload = {
            'type': 'train',    # 'train' or 'apply', depending on frontend message
            'data': self.result
        }
        self.socketio.emit('done', done_payload, to=self.name)


@my_socketio.on('connect')
def handle_connect():
    print('[Server] SocketIO connection established.')
    # 创建 thread
    cur_socket_id = str(request.sid)
    t = ModelThread(my_socketio, name=cur_socket_id)
    threads_dict[cur_socket_id] = t
    # ? DEBUG
    print('cur_socket_id: ', cur_socket_id)
    server_msg = '[Server] Client connected.'
    my_socketio.send(server_msg, to=request.sid)
    # ? DEBUG
    print(server_msg)


@my_socketio.on('disconnect')
def handle_disconnect():
    cur_socket_id = str(request.sid)
    t = threads_dict[cur_socket_id]
    t.stop()
    threads_dict.pop(cur_socket_id)
    # TODO 资源释放，thread
    server_msg = '[Server] Client disconnected.'
    my_socketio.send(server_msg, to=request.sid)
    # ? DEBUG
    print(server_msg)


@my_socketio.on('run')
def handle_run(data):
    cur_socket_id = str(request.sid)
    t = threads_dict[cur_socket_id]
    t.start()
    server_msg = '[Run] Model mission start.'
    my_socketio.send(server_msg, to=request.sid)
    # ? DEBUG
    print(server_msg)
    # TODO 处理负载，决定采用哪种运行方式 (train/apply)
    # ? DEBUG
    print('++++++++++ model run ++++++++++')
    print(type(data))
    print(data)
    print('++++++++++ model run ++++++++++')


@my_socketio.on('retry')
def handle_retry():
    # TODO 更新出错，重新向服务端发送 retry 请求，负载是请求的文件，服务端按需重新运行或发送，直到成功
    pass


if __name__ == '__main__':
    app = create_app()
    eventlet.monkey_patch()
    my_socketio.init_app(app, async_mode='eventlet', transports=['websocket'], cors_allowed_origins='*', logger=True)
    my_socketio.run(app, host='0.0.0.0', port=5000, debug=True)