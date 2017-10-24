from setuptools import setup

setup(
    name='scuevals-api',
    packages=['scuevals_api'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'app=scuevals_api.cmd:cli'
        ]
    },
    install_requires=[
        'beautifulsoup4==4.6.0',
        'blinker==1.4',
        'Flask-Caching==1.3.3',
        'Flask-Cors==3.0.3',
        'Flask-JWT-Extended==3.3.4',
        'Flask-Migrate==2.0.4',
        'Flask-RESTful==0.3.6',
        'Flask-SQLAlchemy==2.2',
        'Flask==0.12.2',
        'gunicorn==19.7.1',
        'psycopg2==2.7.1',
        'python-jose==1.4.0',
        'PyYAML==3.12',
        'requests==2.18.4',
        'rollbar==0.13.16',
        'vcrpy==1.11.1',
        'webargs==1.8.1',
    ],
)
