from flask import Blueprint
from flask_caching import Cache
from flask_jwt_extended import JWTManager

auth_bp = Blueprint('auth', __name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
jwtm = JWTManager()

from .decorators import auth_required  # noqa
from . import jwt  # noqa
from . import views  # noqa
