web: gunicorn core.wsgi
worker: celery -A core.celery worker --pool=solo -l info
release: python manage.py migrate

