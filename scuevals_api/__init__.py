import logging
import os
from flask import Flask

from scuevals_api.models import models_bp, db
from scuevals_api.auth import auth_bp
from scuevals_api.resources import resources_bp
from scuevals_api.errors import get_http_exception_handler


def create_app(config='development'):
    app = Flask(__name__)

    load_config(app, 'default')
    load_config(app, config)

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

    if 'ENV' in app.config and app.config['ENV'] == 'production':
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


def register_error_handler(app):
    app.handle_http_exception = get_http_exception_handler(app)


def load_config(app, config):
    config_dir = os.path.join(os.path.dirname(app.root_path), 'config')
    app.config.from_pyfile(os.path.join(config_dir, config + '.py'))
