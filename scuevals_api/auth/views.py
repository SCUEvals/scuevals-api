import json
import os
import requests
from datetime import timedelta
from flask import jsonify, current_app as app
from flask_jwt_extended import create_access_token, jwt_required, current_user
from jose import jwt, JWTError, ExpiredSignatureError
from marshmallow import fields
from sqlalchemy.orm import subqueryload
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, HTTPException, InternalServerError

from . import auth_bp, cache
from .decorators import auth_required
from scuevals_api.models import Student, User, db, Permission, APIKey, OfficialUserType
from scuevals_api.utils import use_args


@auth_bp.route('/auth', methods=['POST'])
@use_args({'id_token': fields.String(required=True)}, locations=('json',))
def auth(args):
    try:
        headers = jwt.get_unverified_header(args['id_token'])
    except JWTError as e:
        raise UnprocessableEntity('invalid id_token: invalid format: {}'.format(e))

    key = cache.get(headers['kid'])
    if not key:
        try:
            refresh_key_cache(cache)
        except HTTPException as e:
            raise InternalServerError('failed to get certificates from Google: {}'.format(e))

    key = cache.get(headers['kid'])

    if not key:
        raise UnprocessableEntity('invalid id_token: unable to get matching key from Google')

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
        raise UnprocessableEntity('invalid id_token: expired')
    except JWTError as e:
        raise UnprocessableEntity('invalid id_token: {}'.format(e))

    if data['hd'] != 'scu.edu':
        raise UnprocessableEntity('invalid id_token: incorrect hd')

    user = User.query.options(
        subqueryload(User.permissions)
    ).with_polymorphic(Student).filter_by(email=data['email']).one_or_none()

    if user is None:
        # new user
        status = 'new'

        # check the official type of the user
        official = OfficialUserType.query.get(data['email'])

        if official.type == 'student':
            user = Student(
                email=data['email'],
                first_name=data['given_name'],
                last_name=data['family_name'],
                picture=data['picture'] if 'picture' in data else None,
                permissions=[Permission.query.get(Permission.Incomplete)],
                university_id=1
            )
        elif official.type == 'faculty':
            # create a normal user account for them
            # they will only be professors once they link up with a professor account
            user = User(
                email=data['email'],
                first_name=data['given_name'],
                last_name=data['family_name'],
                picture=data['picture'] if 'picture' in data else None,
                permissions=[Permission.query.get(Permission.ReadEvaluations)],
                university_id=1
            )

        else:
            # we do not support other kinds of users
            return jsonify({'status': 'invalid user type'}), 403

        db.session.add(user)
        db.session.flush()
    else:
        # existing user
        status = 'ok'

        # check if user is suspended
        if user.suspended():
            return jsonify({'status': 'suspended', 'until': user.suspended_until.isoformat()}), 401

        # make sure the permissions are correct in case the student lost reading access
        if user.type == User.Student:
            user.check_read_access()

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
@auth_required
def validate():
    new_token = create_access_token(identity=current_user.to_dict())
    return jsonify({'jwt': new_token})


@auth_bp.route('/auth/refresh')
@jwt_required
def refresh():
    if current_user.suspended():
        return jsonify({'status': 'suspended', 'until': current_user.suspended_until.isoformat()}), 401

    if current_user.type == User.Student:
        current_user.check_read_access()

    db.session.commit()

    new_token = create_access_token(identity=current_user.to_dict())
    return jsonify({'jwt': new_token})


@auth_bp.route('/auth/api', methods=['POST'])
@use_args({'api_key': fields.String(required=True)}, locations=('json',))
def auth_api(args):
    key = APIKey.query.filter(APIKey.key == args['api_key']).one_or_none()

    if key is None:
        raise Unauthorized('invalid api key')

    token = create_access_token(identity=key.identity(), expires_delta=timedelta(hours=24))

    return jsonify({'jwt': token})


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
