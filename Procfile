web: gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT app:app
worker: celery -A celery_worker.celery_app worker --loglevel=info
web: python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
