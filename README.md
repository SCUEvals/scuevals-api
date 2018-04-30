[![CircleCI Status for SCUEvals/scuevals-api](https://img.shields.io/circleci/project/github/SCUEvals/scuevals-api/master.svg)](https://app.codeship.com/projects/251868)
[![Coverage Status](https://img.shields.io/coveralls/github/SCUEvals/scuevals-api/master.svg)](https://coveralls.io/github/SCUEvals/scuevals-api?branch=master)
![Code Climate](https://img.shields.io/codeclimate/maintainability/SCUEvals/scuevals-api.svg)
[![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](https://github.com/SCUEvals/scuevals-api/blob/master/LICENSE)

## Running the API
1. Install the app and its dependencies by running `pip install -e .` in the root folder.
1. Set the following environment variables:
   * `DATABASE_URL=<DB URL>`
   * `FLASK_ENV=development`  (options: production, development, test)
   * `JWT_SECRET_KEY=<256-BIT SECRET>`
   * `GOOGLE_CLIENT_ID=<YOUR ID>`
1. Initialize the database by running `app initdb`.
1. Run `app run` to start the API server.

## Running the Tests
Run `python setup.py test`.

## Documentation
The API documentation is available [on Apiary](https://scuevals.docs.apiary.io/).
Documentation for branches other than master can be 
found at [scuevals.github.io/scuevals-api/?branch=nameofbranch](https://scuevals.github.io/scuevals-api/?branch=develop).