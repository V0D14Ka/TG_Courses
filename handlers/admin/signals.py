from typing import List
from tortoise.signals import post_save
from DB.models import Courses
from tasks.tasks import on_update_course_task, on_create_course_task


@post_save(Courses)
async def signal_post_save(
        sender: "Type[Courses]",
        instance: Courses,
        created: bool,
        using_db: "Optional[BaseDBAsyncClient]",
        update_fields: List[str],
) -> None:
    if created:
        print(instance.id)
        on_create_course_task.apply_async(args=(instance.id, instance.title), countdown=60)
    else:
        print(instance.id)
        on_update_course_task.delay(instance.id, instance.title)

