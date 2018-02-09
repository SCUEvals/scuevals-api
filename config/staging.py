import os

ENV = 'staging'
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
ROLLBAR_TOKEN = os.environ['ROLLBAR_API_KEY']
ROLLBAR_ENV = 'staging'
