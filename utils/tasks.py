from DB.models import Users, Courses
from create_bot import bot


async def get_users(item_id):
    """
        Получение queryset пользователей подписанных на курс
    """
    return await Users.filter(courses=item_id)


# Потом поменяю вывод
async def send_mesg(user_id, title):
    """
        Отправка сообщения об изменении курса
    """
    await bot.send_message(user_id, f"Курс {title} был изменен.")


async def send_schedule_mesg(item_id, mesg):
    """
        Отправка сообщения о приближении курса (24 часа)
    """
    await bot.send_message(item_id, mesg)


async def get_course(item_id):
    """
        Получение курса
    """
    return await Courses.get(id=item_id)
