import json
import os
import datetime
import requests
from flask import Blueprint, jsonify, current_app as app
from flask_caching import Cache
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
from jose import jwt, JWTError, ExpiredSignatureError
from marshmallow import fields
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, HTTPException, InternalServerError

from scuevals_api.models import Student, User, db, Role, APIKey
from scuevals_api.utils import use_args

auth_bp = Blueprint('auth', __name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
jwtm = JWTManager()


@auth_bp.route('/auth', methods=['POST'])
@use_args({'id_token': fields.String(required=True)}, locations=('json',))
def auth(args):
    try:
        headers = jwt.get_unverified_header(args['id_token'])
    except JWTError as e:
        raise UnprocessableEntity('invalid id_token format: {}'.format(e))

    key = cache.get(headers['kid'])
    if not key:
        try:
            refresh_key_cache(cache)
        except HTTPException as e:
            raise InternalServerError('failed to get certificates from Google: {}'.format(e))

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
        raise Unauthorized('token is expired')
    except JWTError as e:
        raise UnprocessableEntity('invalid id_token: {}'.format(e))

    if data['hd'] != 'scu.edu':
        raise UnprocessableEntity('invalid id_token')

    user = User.query.filter_by(email=data['email']).one_or_none()

    if user is None:
        # new user
        status = 'new'

        # assume new user is a student for now
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


@auth_bp.route('/auth/validate')
@jwt_required
def validate():
    ident = get_jwt_identity()
    new_token = create_access_token(identity=ident)

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


def refresh_key_cache(data_store):
    jwks = get_certs()
    for key in jwks['keys']:
        data_store.set(key['kid'], key)


def get_certs():
    resp = requests.get('https://accounts.google.com/.well-known/openid-configuration')
    if resp.status_code != 200:
        raise HTTPException('failed to get Google openid config')

    certs_url = resp.json()['jwks_uri']

    resp = requests.get(certs_url)
    if resp.status_code != 200:
        raise HTTPException('failed to get Google JWKs')

    return resp.json()


def validate_university_id(u_id):
    ident = get_jwt_identity()

    if u_id != ident['university_id']:
        raise Unauthorized('not allowed to access resource from another university')
