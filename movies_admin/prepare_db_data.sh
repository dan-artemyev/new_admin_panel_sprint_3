#!/bin/bash
echo "Entering script..."

timeout 30 bash -c 'until nc -zv $DB_HOST $DB_PORT; do sleep 1; done'

if [ $? -eq 0 ]; then
  echo "Database is available, running migrations..."
  python manage.py collectstatic --noinput
  python manage.py migrate
  python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL

  echo "Migrations complete, running sqlite_to_postgres.py..."
  python sqlite_to_postgres/load_data.py
  echo "Data successfully added..."

else
  echo "Timeout waiting for database to start"
  exit 1
fi

exec "$@"