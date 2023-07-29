import datetime
from typing import List
from tortoise.signals import post_save
from DB.models import Courses
from tasks.tasks import on_update_course_task, schedule_course_task
from utils.schedule import convert_string_to_datetime, check_time


@post_save(Courses)
async def signal_post_save(
        sender: "Type[Courses]",
        instance: Courses,
        created: bool,
        using_db: "Optional[BaseDBAsyncClient]",
        update_fields: List[str],
) -> None:
    # Сохранен только что созданный курс
    if created:

        # Курс открыт для записи и есть расписание
        sec = await check_time(instance)
        if sec != -1:
            schedule_course_task.apply_async(args=(instance.id, instance.title), countdown=sec)

    # Иначе курс был обновлен
    else:
        on_update_course_task.delay(instance.id, instance.title)
