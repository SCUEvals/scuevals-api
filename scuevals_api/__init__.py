import os
import datetime
from flask import Flask
from flask_jwt_simple import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
app.config['JWT_EXPIRES'] = datetime.timedelta(days=30)

api = Api(app)
CORS(app)
JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import scuevals_api.cmd # noqa
import scuevals_api.api # noqa
import scuevals_api.exceptions # noqa
