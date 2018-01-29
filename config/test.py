import os

ENV = 'test'
SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
TESTING = True
ROLLBAR_TOKEN = os.environ['ROLLBAR_API_KEY']
ROLLBAR_ENV = 'test'
