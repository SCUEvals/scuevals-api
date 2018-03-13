release: alembic upgrade head
web: newrelic-admin run-program gunicorn "scuevals_api:create_app(\"$FLASK_ENV\")"