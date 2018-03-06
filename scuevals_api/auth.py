import json
import os
import requests
from datetime import timedelta
from flask import Blueprint, jsonify, current_app as app
from flask_caching import Cache
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from jose import jwt, JWTError, ExpiredSignatureError
from marshmallow import fields
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, HTTPException, InternalServerError

from scuevals_api.models import Student, User, db, Permission, APIKey, OfficialUserType
from scuevals_api.models.api_key import API_KEY_TYPE
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
        decode_options['verify_aud'] = False

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

    user = User.query.options(
        subqueryload(User.permissions)
    ).with_polymorphic(Student).filter_by(email=data['email']).one_or_none()

    if user is None:
        # new user
        status = 'new'

        # check the official type of the user
        official = OfficialUserType.query.get(data['email'])

        if official is None or official.type != 'student':
            # create a user
            # but for now, return message
            return jsonify({'status': 'non-student'}), 403
        else:
            user = Student(
                email=data['email'],
                first_name=data['given_name'],
                last_name=data['family_name'],
                picture=data['picture'] if 'picture' in data else None,
                permissions=[Permission.query.get(Permission.Incomplete)],
                university_id=1
            )

        db.session.add(user)
        db.session.flush()
    else:
        # existing user
        status = 'ok'

        # check if user is suspended
        if user.suspended():
            return jsonify({'status': 'suspended', 'until': user.suspended_until.isoformat()}), 401

        # check if they should be unsuspended
        if user.suspension_expired():
            user.suspended_until = None

        # make sure the permissions are correct in case the student lost reading access
        if user.type == User.Student and not user.has_reading_access():
            user.permissions = [permission for permission in user.permissions if
                                permission.id not in [Permission.ReadEvaluations, Permission.VoteOnEvaluations]]

            user.read_access_until = None

        # update the image of the existing user
        if 'picture' in data:
            user.picture = data['picture']

        # check if user is complete
        if Permission.Incomplete in user.permissions_list:
            status = 'incomplete'

    token = create_access_token(identity=user.to_dict())

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

    token = create_access_token(identity=key.identity(), expires_delta=timedelta(hours=24))

    return jsonify({'jwt': token})


@jwtm.claims_verification_loader
def claims_verification_loader(user_claims):
    identity = get_jwt_identity()

    keys = [
        'type',
        'permissions',
        'university_id'
    ]

    for key in keys:
        if key not in identity:
            return False

    return True


@jwtm.claims_verification_failed_loader
def claim_verification_failed():
    return jsonify({'message': 'invalid or expired user info'}), 401


@jwtm.user_loader_callback_loader
def user_loader(identity):
    if identity['type'] == API_KEY_TYPE:
        return 1

    user = load_user(identity['id'])

    # fail if the user is still suspended
    if user.suspended():
        return None

    # fail if the JWT doesn't reflect that the user lost reading access
    if Permission.ReadEvaluations in identity['permissions'] and not user.has_reading_access():
        return None

    return user


def load_user(user_id):
    return User.query.options(
        subqueryload(User.permissions)
    ).with_polymorphic(Student).filter(User.id == user_id).one_or_none()


@jwtm.user_loader_error_loader
def user_loader_error(identity):
    return jsonify({'message': 'invalid or expired user info'}), 401


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
