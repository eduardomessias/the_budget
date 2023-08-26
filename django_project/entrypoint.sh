#!/bin/sh

# wait for PSQL server to start
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Make migrations
echo "Making migrations"
python manage.py makemigrations --noinput

# Run migrations
echo "Running migrations"
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

exec "$@"
