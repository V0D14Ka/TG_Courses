import tortoise
import os

from tortoise.signals import post_save

from DB.models import Courses
from tortoise.signals import post_save
from typing import List, Optional, Type
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient


async def db_init():
    # con = sqlite3.connect("sqlite.db")
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await tortoise.Tortoise.init(
        db_url="postgres://root:root@pg_db:5432/bot_db",
        modules={'models': ['DB.models']}
    )
    # # Generate the schema
    await tortoise.Tortoise.generate_schemas()


@post_save(Courses)
async def signal_post_save(
        sender: "Type[Courses]",
        instance: Courses,
        created: bool,
        using_db: "Optional[BaseDBAsyncClient]",
        update_fields: List[str],
) -> None:
    raise Exception(sender, instance, using_db, created, update_fields)

# Объявляем сигнал
# @post_save(Courses)
# async def course_updated(sender, instance, **kwargs):
#     # Ваш код для обработки изменения курса
#     # Вызов функции оповещения пользователей при изменении курса
#     raise Exception("IDI NAHUI")
