#!/bin/bash

# Esperar a que la base de datos esté lista
if [ "$DATABASE" = "postgres" ]
then
    echo "Esperando a postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "Postgres está listo"
fi

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

exec "$@"
