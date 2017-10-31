import json
import os
import datetime
import requests
from flask import Blueprint, jsonify, current_app as app
from flask_caching import Cache
from flask_jwt_extended import create_access_token, decode_token, JWTManager, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError
from jose import jwt, JWTError, ExpiredSignatureError
from marshmallow import fields
from werkzeug.exceptions import UnprocessableEntity, Unauthorized

from scuevals_api.models import Student, db, Role, APIKey
from scuevals_api.utils import use_args

auth_bp = Blueprint('auth', __name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
jwtm = JWTManager()


@auth_bp.route('/auth', methods=['POST'])
@use_args({'id_token': fields.String(required=True)}, locations=('json',))
def auth(args):
    headers = jwt.get_unverified_header(args['id_token'])

    key = cache.get(headers['kid'])
    if not key:
        refresh_key_cache()

    key = cache.get(headers['kid'])

    decode_options = {'verify_at_hash': False}

    if app.debug:
        decode_options['verify_exp'] = False

    try:
        data = jwt.decode(
            args['id_token'],
            json.dumps(key),
            audience=os.environ['GOOGLE_CLIENT_ID'],
            issuer=('https://accounts.google.com', 'accounts.google.com'),
            options=decode_options
        )
    except ExpiredSignatureError:
        raise Unauthorized(description='token is expired')
    except JWTError as e:
        raise UnprocessableEntity(description='invalid id_token: {}'.format(e))

    # TODO: Get this value from the database
    # essentially, the only way to figure out which university
    # the student is allowed/supposed to sign up for, is to check
    # which domain the request came from (needs to be HTTPS as well)
    # there also needs to be a debug mode where this verification is skipped
    if data['hd'] != 'scu.edu':
        raise UnprocessableEntity(description='invalid id_token')

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
@use_args({'jwt': fields.String(required=True)}, locations=('json',))
def validate(args):
    try:
        data = decode_token(args['jwt'])
    except JWTDecodeError:
        raise Unauthorized('invalid jwt')

    new_token = create_access_token(identity=data['sub'])

    return jsonify({'jwt': new_token})


@auth_bp.route('/auth/api', methods=['POST'])
@use_args({'api_key': fields.String(required=True)}, locations=('json',))
def auth_api(args):
    key = APIKey.query.filter(APIKey.key == args['api_key']).one_or_none()

    if key is None:
        raise Unauthorized('invalid api key')

    ident = {
        'university_id': key.university_id,
        'roles': [20]
    }

    token = create_access_token(identity=ident, expires_delta=datetime.timedelta(hours=24))

    return jsonify({'jwt': token})


@jwtm.claims_verification_loader
def claims_verification_loader(user_claims):
    identity = get_jwt_identity()
    if 'university_id' not in identity or 'roles' not in identity:
        return False
    return True


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
