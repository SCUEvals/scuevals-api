import os
import time
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_simple import create_jwt
from flask_restful import fields
from webargs.flaskparser import use_kwargs
from scuevals_api.errors import BadRequest

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
        raise BadRequest('inavlid id_token')

    # TODO: Get this value from the database
    if data['hd'] != 'scu.edu':
        raise BadRequest('inavlid id_token')

    jwt = create_jwt(identity=data['email'])

    return jsonify({'jwt': jwt})
