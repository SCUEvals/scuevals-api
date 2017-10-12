import datetime
import os
from flask import Flask

from scuevals_api.auth import auth_bp
from scuevals_api.resources import resources_bp
from scuevals_api.errors import errors_bp


def create_app(config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
    app.config['JWT_EXPIRES'] = datetime.timedelta(days=30)

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

    from flask_jwt_simple import JWTManager
    JWTManager(app)

    from scuevals_api.auth import cache
    cache.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(errors_bp)


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
