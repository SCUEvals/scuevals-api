[![Codeship Status for SCUEvals/scuevals-api](https://img.shields.io/codeship/79c54590-9792-0135-c174-3eb644f498b4/master.svg)](https://app.codeship.com/projects/251868) 
[![Coverage Status](https://img.shields.io/coveralls/github/SCUEvals/scuevals-api/master.svg)](https://coveralls.io/github/SCUEvals/scuevals-api?branch=master)

## Running the API
1. Install the app and its dependencies by running `pip install -e .` in the root folder.
1. Set the following environment variables:
   * `FLASK_APP=scuevals_api`
   * `DATABASE_URL=<DB URL>`
   * `FLASK_CONFIG=development`  (options: production, development, test)
   * `JWT_SECRET_KEY=<256-BIT SECRET>`
   * `GOOGLE_CLIENT_ID=<YOUR ID>`
1. Initialize the database by running `app initdb`.
1. Seed the database by running `app seeddb`.
1. Run `app run` to start the API server.

## Running the Tests
Run `python setup.py test`.

## Documentation
The API documentation is available [on Apiary](https://scuevals.docs.apiary.io/).