from setuptools import setup

setup(
    name='scuevals-api',
    packages=['scuevals_api'],
    include_package_data=True,
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'app=scuevals_api.cmd:cli'
        ]
    },
    install_requires=[
        'alembic==0.9.9',
        'beautifulsoup4==4.6.0',
        'blinker==1.4',
        'coveralls==1.3.0',
        'dredd_hooks==0.2.0',
        'factory_boy==2.10.0',
        'Flask-Caching==1.4.0',
        'Flask-Cors==3.0.4',
        'Flask-JWT-Extended==3.8.1',
        'Flask-Migrate==2.1.1',
        'Flask-RESTful==0.3.6',
        'Flask-Rollbar==1.0.1',
        'Flask-SQLAlchemy==2.3.2',
        'Flask==1.0.1',
        'freezegun==0.3.10',
        'gunicorn==19.8.1',
        'jsonschema==2.6.0',
        'newrelic==3.2.0.91',
        'psycopg2==2.7.4',
        'pycryptodome>=3.4.7',
        'python-jose==2.0.2',
        'pytz==2018.4',
        'PyYAML==3.12',
        'requests==2.18.4',
        'rollbar==0.13.18',
        'sqlalchemy-views==0.2.1',
        'vcrpy==1.11.1',
        'webargs==2.1.0',
    ],
)
