import os
import time
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_simple import create_jwt, decode_jwt
from webargs.flaskparser import use_kwargs
from webargs import missing, fields
from scuevals_api.models import Student, db
from scuevals_api.errors import BadRequest, Unauthorized

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth', methods=['POST'])
@use_kwargs({'id_token': fields.String()})
def auth(id_token):
    if request.headers['Content-Type'] != 'application/json':
        raise BadRequest('wrong mime type')

    resp = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo', params={'id_token': id_token})

    if resp.status_code != 200:
        raise BadRequest('failed to validate id_token with Google')

    data = resp.json()
    if data['iss'] not in ('https://accounts.google.com', 'accounts.google.com'):
        raise BadRequest('invalid id_token')

    if data['aud'] != os.environ['GOOGLE_CLIENT_ID']:
        raise BadRequest('invalid id_token')

    if float(data['exp']) < time.time():
        raise BadRequest('invalid id_token')

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
            university_id=1
        )

        db.session.add(user)
        db.session.flush()
    else:
        # check if user is complete
        if user.graduation_year is None:
            status = 'incomplete'
            user.first_name = data['given_name']
            user.last_name = data['family_name']
        else:
            status = 'ok'

    ident = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    }

    jwt = create_jwt(identity=ident)

    db.session.commit()

    return jsonify({'status': status, 'jwt': jwt})


@auth_bp.route('/auth/validate', methods=['POST'])
@use_kwargs({'jwt': fields.String()})
def validate(jwt):
    if jwt is missing:
        raise BadRequest('missing jwt paramter')

    try:
        decode_jwt(jwt)
    except:
        raise Unauthorized('invalid jwt')
    return jsonify({'jwt': jwt})
