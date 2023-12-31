# -*- coding: utf-8 -*-
import os
import click
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

import eventlet
from flask import Flask, request

from blueprints.user import user_bp
from blueprints.model import model_bp
from models import Admin, User, PaddleModel, BindingModel
from extensions import login_manager, db, sess, cors, my_socketio
from settings import configs

# * SocketIO configs
from api.sio import *

basedir = os.path.abspath(os.path.dirname(__file__))


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
    @click.option('--user', default=4, help='Quantity of users, default is 4.')
    @click.option('--model', default=5, help='Quantity of models, default is 3.')
    @click.option('--bindings', default=0, help='Quantity of bindings, default is 0.')
    def forge(user, model, bindings):
        """Generate fake data."""
        from fakes import fake_admin, fake_users, fake_models, fake_bindings

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
    # init login_manager
    login_manager.init_app(app)
    # init database
    db.init_app(app)
    # init session
    sess.init_app(app)
    # init cors
    cors.init_app(app)
    # init socketio
    my_socketio.init_app(app, async_mode='eventlet', transports=['websocket'], cors_allowed_origins='*', logger=True)


def register_blueprints(app: Flask):
    """ 蓝本模块 """
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(model_bp, url_prefix='/model')


if __name__ == '__main__':
    app = create_app()
    eventlet.monkey_patch()
    my_socketio.run(app, host='0.0.0.0', port=5000, debug=True)