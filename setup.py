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
        'alembic==0.9.7',
        'beautifulsoup4==4.6.0',
        'blinker==1.4',
        'coveralls==1.2.0',
        'Flask-Caching==1.3.3',
        'Flask-Cors==3.0.3',
        'Flask-JWT-Extended==3.6.0',
        'Flask-Migrate==2.1.1',
        'Flask-RESTful==0.3.6',
        'Flask-Rollbar==1.0.1',
        'Flask-SQLAlchemy==2.3.2',
        'Flask==0.12.2',
        'gunicorn==19.7.1',
        'newrelic==2.100.0.84',
        'psycopg2==2.7.3.2',
        'pycryptodome>=3.4.7'
        'python-jose==2.0.1',
        'PyYAML==3.12',
        'requests==2.18.4',
        'rollbar==0.13.17',
        'vcrpy==1.11.1',
        'webargs==1.8.1',
    ],
)
