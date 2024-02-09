import os

from celery.app import Celery

redis_url = os.getenv("REDIS_URL", "redis://mail-redis:6379")
broker_url = os.getenv("REDIS_URL", "amqp://mailexport:m@ilexp0rt@mail-rabbitmq")

celery_app = Celery(__name__, broker=broker_url, backend=redis_url, include=['tasks.migrate', 'tasks.signals'])

