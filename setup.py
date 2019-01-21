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
        'alembic==1.0.5',
        'beautifulsoup4==4.6.3',
        'blinker==1.4',
        'coveralls==1.5.1',
        'cryptography==2.4.2',
        'dredd_hooks==0.2.0',
        'factory_boy==2.11.1',
        'Flask-Caching==1.4.0',
        'Flask-Cors==3.0.7',
        'Flask-JWT-Extended==3.14.0',
        'Flask-Migrate==2.3.1',
        'Flask-RESTful==0.3.6',
        'Flask-Rollbar==1.0.1',
        'Flask-SQLAlchemy==2.3.2',
        'Flask==1.0.2',
        'freezegun==0.3.11',
        'gunicorn==19.9.0',
        'jsonschema==2.6.0',
        'newrelic==4.8.0.110',
        'psycopg2==2.7.6.1',
        'python-jose==3.0.1',
        'pytz==2018.7',
        'PyYAML==3.13',
        'requests==2.21.0',
        'rollbar==0.14.5',
        'sqlalchemy-views==0.2.2',
        'vcrpy==2.0.1',
        'webargs==4.1.3',
    ],
    extras_require={
        'dev': [
            'flake8'
        ]
    }
)
