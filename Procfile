web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput && (python manage.py createsuperuser --noinput 2>/dev/null; true)
