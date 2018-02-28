import os

ENV = 'test'
SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
TESTING = True
DEBUG = True
