import types

from celery import Celery, shared_task
import os

import asyncio

from dotenv import load_dotenv
from tortoise import Tortoise

from DB.models import Users
from create_bot import bot
from asgiref.sync import async_to_sync


async def db_init():
    await Tortoise.init(
        db_url="postgres://root:root@pg_db:5432/bot_db",
        modules={'models': ['DB.models']}
    )


load_dotenv()
celery = Celery('TG_university')
celery.autodiscover_tasks()
async_to_sync(db_init)()

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
celery.config_from_object('tasks:tasks', namespace='CELERY')

celery_event_loop = asyncio.new_event_loop()


@celery.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


async def get_users(item_id):
    return await Users.filter(courses=item_id)


async def send_mesg(user_id, title):
    await bot.send_message(user_id, f"Курс {title} был изменен.")


@shared_task
def on_update_course_task(item_id, title):
    users = celery_event_loop.run_until_complete(get_users(item_id))
    for i in users:
        celery_event_loop.run_until_complete(send_mesg(i.id, title))
