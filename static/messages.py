# Information
from DB.models import Users

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
ask_for_update_course = '''
Для отмены напишите - "Отмена".
Текущее значение: %s. 
Введите новое значение: '''

ask_for_update_user_info = '''
Шаг %s/9.
Введите %s.
Пример : %s.
Для отмены напишите "Отмена". 
Обращаю ваше внимание: в случае отмены весь прогресс будет утерян.
'''


def make_item_info(item, updated):  # Сборка информации о курсе
    answer = item_info % (item[1], item[2], item[3],
                          item[4], item[5], item[6])
    if updated:
        return "Изменение прошло успешно:\n" + answer
    else:
        return answer


async def make_user_info(item: Users, updated):  # Сборка информации о студенте
    passport = str(item.passport_data) + str(item.passport_date) + str(item.passport_issued) + str(item.department_code)
    answer = user_info % (item.full_name, item.study_group, item.phone_number,
                          item.date_of_birth, passport, item.place_of_registration)
    if updated:
        return "Изменение прошло успешно:\n" + answer
    else:
        return answer


def make_ask_for_update_course(current_val):
    return ask_for_update_course % current_val
