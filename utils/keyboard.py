from aiogram.types import InlineKeyboardButton


async def print_list_courses(make_callback_data, markup, courses, category, current_level, offset=0):
    """
    Процедура отрисовки кнопок в клавиатуру - курсов.

    :param make_callback_data: Функция класса по составлению callback_data.
    :param markup: Клавиатура для вставки.
    :param courses: Список Courses.
    :param category: Категория меню.
    :param current_level: Текущий уровень меню.
    :param offset: Сдвиг для запроса курсов из бд.
    """
    for course in courses:
        print(course.title)
        button_text = f"{course.title}"
        callback_data = make_callback_data(category=category, level=current_level + 1,
                                           item_id=course.id, offset=int(offset))

        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
