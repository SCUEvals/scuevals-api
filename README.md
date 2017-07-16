## Running the API
1. Install the app and its dependencies by running `pip install -e .` in the root folder.
1. Set the `DATABASE_URL` enviroment variable.
1. Set the following environment variables:
   * `FLASK_APP=scuevals_api`
   * `DATABASE_URL=<db connection url>`
1. Initialize the database by running `flask initdb`
1. Run `flask run` to start the API server.

