from setuptools import setup

setup(
    name='scuevals-api',
    packages=['scuevals_api'],
    include_package_data=True,
    install_requires=[
        'Flask-Cors==3.0.3',
        'Flask-Migrate==2.0.4',
        'Flask-RESTful==0.3.6',
        'Flask-SQLAlchemy==2.2',
        'Flask==0.12.2',
        'gunicorn==19.7.1',
        'psycopg2==2.7.1'
    ],
)