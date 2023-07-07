# -*- coding: utf-8 -*-
import os
import click
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, request

from backend.blueprints.user import user_bp
from backend.blueprints.model import model_bp
from backend.models import User, PaddleModel, BindingModel
from backend.extensions import db
from backend.settings import configs

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

    file_handler = RotatingFileHandler(
        os.path.join(basedir, 'logs/wpf_system.log'), maxBytes=10 * 1024 * 1024, backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    if not app.debug:
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


def register_extensions(app: Flask):
    """ 扩展模块 """
    db.init_app(app) # init database


def register_blueprints(app: Flask):
    """ 蓝本模块 """
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(model_bp, url_prefix='/model')


if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)