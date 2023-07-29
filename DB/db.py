import tortoise


async def db_init():
    # Here we connect to DB.
    # also specify the app name of "models"
    # which contain models from "DB.models"
    await tortoise.Tortoise.init(
        db_url="postgres://root:root@pg_db:5432/bot_db",
        modules={'models': ['DB.models']}
    )
    # # Generate the schema
    await tortoise.Tortoise.generate_schemas()

