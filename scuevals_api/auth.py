import json
import os
import datetime
import requests
from flask import Blueprint, request, jsonify
from flask_caching import Cache
from flask_jwt_extended import create_access_token, decode_token, JWTManager
from jose import jwt, JWTError
from marshmallow import fields
from webargs.flaskparser import use_kwargs
from webargs import missing

from scuevals_api.models import Student, db, Role, APIKey
from scuevals_api.errors import BadRequest, Unauthorized

auth_bp = Blueprint('auth', __name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
jwtm = JWTManager()


@auth_bp.route('/auth', methods=['POST'])
@use_kwargs({'id_token': fields.String()})
def auth(id_token):
    if request.headers['Content-Type'] != 'application/json':
        raise BadRequest('wrong mime type')

    if id_token is missing:
        raise BadRequest('missing id_token')

    headers = jwt.get_unverified_header(id_token)

    key = cache.get(headers['kid'])
    if not key:
        refresh_key_cache()

    key = cache.get(headers['kid'])

    try:
        data = jwt.decode(
            id_token,
            json.dumps(key),
            audience=os.environ['GOOGLE_CLIENT_ID'],
            issuer=('https://accounts.google.com', 'accounts.google.com'),
            options={'verify_at_hash': False}
        )
    except JWTError as e:
        raise BadRequest('invalid id_token: {}'.format(e))

    # TODO: Get this value from the database
    # essentially, the only way to figure out which university
    # the student is allowed/supposed to sign up for, is to check
    # which domain the request came from (needs to be HTTPS as well)
    # there also needs to be a debug mode where this verification is skipped
    if data['hd'] != 'scu.edu':
        raise BadRequest('invalid id_token')

    user = Student.query.filter_by(email=data['email']).one_or_none()

    if user is None:
        # new user
        status = 'new'

        user = Student(
            email=data['email'],
            first_name=data['given_name'],
            last_name=data['family_name'],
            picture=data['picture'] if 'picture' in data else None,
            roles=[Role.query.get(Role.Incomplete)],
            university_id=1
        )

        db.session.add(user)
        db.session.flush()
    else:
        # update the image of the existing user
        if 'picture' in data:
            user.picture = data['picture']

        # check if user is complete
        if Role.Incomplete in user.roles_list:
            status = 'incomplete'
        else:
            status = 'ok'

    ident = user.to_dict()

    token = create_access_token(identity=ident)

    db.session.commit()

    return jsonify({'status': status, 'jwt': token})


@auth_bp.route('/auth/validate', methods=['POST'])
@use_kwargs({'jwt': fields.String(required=True)})
def validate(jwt):
    try:
        data = decode_token(jwt)
    except:
        raise Unauthorized('invalid jwt')

    new_token = create_access_token(identity=data['sub'])

    return jsonify({'jwt': new_token})


@auth_bp.route('/auth/api', methods=['POST'])
@use_kwargs({'api_key': fields.String(required=True)})
def auth_api(api_key):
    key = APIKey.query.filter(APIKey.key == api_key).one_or_none()

    if key is None:
        raise Unauthorized('invalid api key')

    ident = {
        'university_id': key.university_id,
        'roles': [20]
    }

    token = create_access_token(identity=ident, expires_delta=datetime.timedelta(hours=24))

    return jsonify({'jwt': token})


@jwtm.user_loader_callback_loader
def user_loader_callback_loader(identity):
    if 'university_id' not in identity or 'roles' not in identity:
        return None
    return {}


@jwtm.user_loader_error_loader
def user_loader_error_loader(identity):
    return jsonify({'error': "missing fields in jwt"}), 422


def refresh_key_cache():
    jwks = get_certs()
    for key in jwks['keys']:
        cache.set(key['kid'], key)


def get_certs():
    resp = requests.get('https://accounts.google.com/.well-known/openid-configuration')
    if resp.status_code != 200:
        raise Exception('failed to get Google openid config')

    certs_url = resp.json()['jwks_uri']

    resp = requests.get(certs_url)
    if resp.status_code != 200:
        raise Exception('failed to get Google JWKs')

    return resp.json()
