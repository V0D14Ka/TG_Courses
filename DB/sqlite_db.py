import tortoise


async def db_init():
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await tortoise.Tortoise.init(
        db_url='sqlite://sqlite.db',
        modules={'models': ['DB.models']}
    )
    # Generate the schema
    await tortoise.Tortoise.generate_schemas()
