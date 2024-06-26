#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
done
echo "PostgreSQL started"


python manage.py collectstatic --no-input \
&& python manage.py migrate \
&& gunicorn --bind 0.0.0.0:8000 foodgram.wsgi

exec "$@"