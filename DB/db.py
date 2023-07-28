import tortoise


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

