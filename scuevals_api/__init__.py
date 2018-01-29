import datetime
import logging
import os
from flask import Flask

from scuevals_api.models import models_bp, db
from scuevals_api.auth import auth_bp
from scuevals_api.resources import resources_bp
from scuevals_api.errors import get_http_exception_handler


class Config:
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=30)
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    ENV = 'test'
    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
    TESTING = True
    ROLLBAR_TOKEN = os.environ['ROLLBAR_API_KEY']
    ROLLBAR_ENV = 'testing'


class DevelopmentConfig(Config):
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    ROLLBAR_TOKEN = os.environ['ROLLBAR_API_KEY']
    ROLLBAR_ENV = 'production'


def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)

    app.config.from_object(config_object)

    if 'ENV' in app.config and app.config['ENV'] == 'test':
        logging.disable(logging.CRITICAL)

    register_error_handler(app)
    register_extensions(app)
    register_blueprints(app)
    register_cli(app)

    return app


def register_extensions(app):
    from flask_migrate import Migrate
    Migrate(app, db)

    from flask_cors import CORS
    CORS(app)

    from scuevals_api.auth import cache, jwtm
    jwtm.init_app(app)
    cache.init_app(app)

    if 'ENV' in app.config and app.config['ENV'] in ('production', 'testing'):
        from scuevals_api.errors import rollbar
        rollbar.init_app(app)


def register_blueprints(app):
    app.register_blueprint(models_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)


def register_cli(app):
    from scuevals_api.models import db

    @app.cli.command(short_help='Initializes the DB.')
    def initdb():
        from scuevals_api.cmd import init_db
        init_db(app, db)

    @app.cli.command(short_help='Seeds the DB.')
    def seeddb():
        from scuevals_api.cmd import seed_db
        seed_db(db)


def register_error_handler(app):
    app.handle_http_exception = get_http_exception_handler(app)
