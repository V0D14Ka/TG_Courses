import types

from celery import Celery, shared_task
import os

import asyncio

from celery.contrib.abortable import AbortableTask
from dotenv import load_dotenv
from tortoise import Tortoise

from DB.models import Users, Courses
from create_bot import bot
from asgiref.sync import async_to_sync
from celery.schedules import crontab

from utils.schedule import check_time


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


@celery.task(bind=True, name="hello")
def debug_task(self):
    print(f'Request: {self.request!r}')


async def get_users(item_id):
    return await Users.filter(courses=item_id)


async def send_mesg(user_id, title):
    await bot.send_message(user_id, f"Курс {title} был изменен.")


@shared_task
def on_update_course_task(item_id, title):
    status, task_id = 0, 0

    # Ищем задание в очереди
    queue = celery.control.inspect().scheduled()
    for i in list(queue.values())[0]:
        if i['request']['args'][0] == item_id:
            status = 200
            task_id = i['request']['id']
            break

    # Нашлось задание об оповещении в очереди, ревокаем и создаем новое
    if status == 200:
        celery.control.revoke(task_id=task_id, terminate=True, signal='SIGKILL')
        course = celery_event_loop.run_until_complete(get_course(item_id))
        sec = celery_event_loop.run_until_complete(check_time(course))

        if sec != -1:
            schedule_course_task.apply_async(args=(item_id, title), countdown=sec)
            # raise Exception(f"Новое уведомление о начале курса {course.title} будет оправлено через {sec}")

    users = celery_event_loop.run_until_complete(get_users(item_id))
    for i in users:
        celery_event_loop.run_until_complete(send_mesg(i.id, title))


async def send_schedule_mesg(item_id, mesg):
    await bot.send_message(item_id, f"Hi {mesg}")


async def get_course(item_id):
    return await Courses.get(id=item_id)


@shared_task(base=AbortableTask)
def schedule_course_task(item_id, title):
    course = celery_event_loop.run_until_complete(get_course(item_id))
    mesg = f"Завтра - {course.schedule} начинается курс по {course.title} в аудитории {course.audience}!"
    users = celery_event_loop.run_until_complete(get_users(item_id))
    for i in users:
        celery_event_loop.run_until_complete(send_schedule_mesg(i.id, mesg))
