#!/bin/sh

host="$1"

echo "Menunggu database di host $host..."

# Tunggu DB siap
until nc -z -q 1 "$host" 5432; do
  echo "Postgres belum siap - sleeping"
  sleep 1
done

echo "Postgres siap! Menjalankan migrate dan runserver..."

# Jalankan migrate dan runserver secara unbuffered supaya log langsung muncul
python -u manage.py makemigrations
python -u manage.py migrate
exec python -u manage.py runserver 0.0.0.0:8000