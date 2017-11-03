import logging
import os
from flask import Flask

from scuevals_api.auth import auth_bp
from scuevals_api.resources import resources_bp
from scuevals_api.errors import get_http_exception_handler


def create_app(config_object=None):
    app = Flask(__name__)
    load_config(app, 'default')

    if 'FLASK_CONFIG' not in os.environ:
        app.config['FLASK_CONFIG'] = 'development'
    else:
        app.config['FLASK_CONFIG'] = os.environ['FLASK_CONFIG']

    try:
        load_config(app, app.config['FLASK_CONFIG'])
    except IOError:
        raise Exception('invalid config specified')

    if app.config['FLASK_CONFIG'] == 'test':
        logging.disable(logging.CRITICAL)

    if config_object is not None:
        app.config.from_object(config_object)

    register_error_handler(app)
    register_extensions(app)
    register_blueprints(app)
    register_cli(app)

    return app


def register_extensions(app):
    from scuevals_api.models import db
    db.init_app(app)

    from flask_migrate import Migrate
    Migrate(app, db)

    from flask_cors import CORS
    CORS(app)

    from scuevals_api.auth import cache, jwtm
    jwtm.init_app(app)
    cache.init_app(app)

    if 'FLASK_CONFIG' in os.environ and os.environ['FLASK_CONFIG'] == 'production':
        from scuevals_api.errors import rollbar
        rollbar.init_app(app)


def register_blueprints(app):
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


def load_config(app, config):
    config_dir = os.path.join(os.path.dirname(app.root_path), 'config')
    app.config.from_pyfile(os.path.join(config_dir, config + '.py'))
