# Information
from DB.models import Users, Courses

welcome_mesg = '''Добро пожаловать в наш бот! Используйте /menu'''
help_mesg = '''Здесь будет инфа о командах бота'''

# Reply exceptions
cant_initiate_conversation = '''Для начала работы со мной напишите мне в ЛС!'''
bot_blocked = "Разблокируйте меня, чтобы продолжить диалог!"
unauthorized = 'Не удалось написать вам!'
went_wrong = 'Что-то пошло не так...'
incorrect_input = '''
Неверный ввод, попробуйте еще раз 
или напишите 'Отмена'!
Ошибка: %s.
Пример : %s.
'''

# Authenticate
ask_for_password = 'Введите пароль:'
already_authenticated = 'Вы авторизированы, как админ. Используйте /menu'

item_info = '''
Информация о курсе:
Предмет - %s.
Расписание - %s.
Цена - %s.
Аудитория - %s.
Преподаватель - %s.
Комментарий - %s.
'''
user_info = '''
Ваши данные:
ФИО - %s.
Группа - %s.
Номер телефона - %s.
Дата рождения - %s.
Паспорт - %s.
Регистрация - %s.
'''
ask_for_update = '''
Для отмены напишите - "Отмена".
Текущее значение: %s. 
Введите новое значение: '''

ask_for_update_user_info = '''
Шаг %s/10.
Введите %s.
Пример : %s.
Для отмены напишите "Отмена". 
Обращаю ваше внимание: в случае отмены весь прогресс будет утерян.
'''


def make_item_info(item: Courses, updated):
    """
    Сборка информации о курсе.
    :param item: Courses.
    :param updated: Флаг - после изменения.
    :return: строка с сообщением.
    """
    answer = item_info % (item.title, ('\n' + item.schedule.replace(";", "\n")) if item.schedule is not None else
                          item.schedule, item.price, item.audience, item.teacher, item.comment)
    if updated:
        return "Изменение прошло успешно:\n" + answer
    else:
        return answer


async def make_user_info(item: Users, updated):
    """
    Сборка информации о студенте.
    :param item: Users.
    :param updated: Флаг - после изменения.
    :return: Строка с сообщением.
    """
    passport = str(item.passport_series) + str(item.passport_number) + "/" + str(item.passport_date) + \
               "/" + str(item.passport_issued) + "/" + str(item.department_code)
    answer = user_info % (item.full_name, item.study_group, item.phone_number,
                          item.date_of_birth, passport, item.reg_place)
    if updated:
        return "Изменение прошло успешно:\n" + answer
    else:
        return answer


def make_ask_for_update(current_val):
    """
    Построение сообщения с просьбой ввести новое значение.
    :param current_val: Текущее значение.
    :return: Строка с сообщением.
    """
    return ask_for_update % current_val
