# Procfile

# Web service: run Django with Gunicorn
web: gunicorn core.wsgi --bind 0.0.0.0:$PORT

# Celery worker for background tasks
worker: celery -A core.celery worker --pool=solo -l info

