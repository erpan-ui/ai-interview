from app.core.celery_app import celery_app

if __name__ == '__main__':
    # This file is used to start Celery workers
    celery_app.start(['celery', 'worker', '--loglevel=info'])