import types

from celery import Celery
import os

import asyncio

from DB.models import Users

celery = Celery('TG_university')
celery.autodiscover_tasks()

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
celery.config_from_object('tasks:tasks', namespace='CELERY')


@celery.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


async def get():
    return await Users.all()


@celery.task
def print_f(u: list[Users]):

    raise Exception(u[0])
