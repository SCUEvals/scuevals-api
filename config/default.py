import datetime
import os

JWT_IDENTITY_CLAIM = 'sub'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=30)
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
SQLALCHEMY_TRACK_MODIFICATIONS = False
