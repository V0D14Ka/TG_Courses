from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


# Класс отображения клавиатур для студента
class InlineStudent:
    menu_cd = CallbackData("show_menu", "level", "category", "item_id", "sub", "offset")
    sub_course_cd = CallbackData("sub", "item_id")

    # Создаем колбек дату
    def make_callback_data(self, level, category=0, item_id=0, is_sub=0, offset=0):
        return self.menu_cd.new(level=level, category=category, item_id=item_id, sub=is_sub, offset=offset)

    # Универсальная клавиатура для уровня 0
    async def menu_keyboard(self):
        current_level = 0
        markup = InlineKeyboardMarkup()

        markup.insert(
            InlineKeyboardButton(text="Открытые курсы", callback_data=self.make_callback_data(level=current_level + 1,
                                                                                              category=1, offset=0))
        )

        markup.insert(
            InlineKeyboardButton(text="Мои курсы", callback_data=self.make_callback_data(level=current_level + 1,
                                                                                         category=2))
        )
        markup.insert(
            InlineKeyboardButton(text="Мои данные", callback_data=self.make_callback_data(level=current_level + 1,
                                                                                          category=3))
        )

        return markup

    # Функция отрисовки кнопок - курсов
    async def print_list_courses(self, markup, courses, category, current_level, offset=0):
        for course in courses:
            print(course.title)
            button_text = f"{course.title}"
            callback_data = self.make_callback_data(category=category, level=current_level + 1,
                                                    item_id=course.id, offset=int(offset))

            markup.insert(
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            )

    # Универсальная клавиатура для уровня 1
    async def category_keyboard(self, category=0, courses=None, user_info=None, empty_info=False, offset=0,
                                end_list=False):
        current_level = 1
        markup = InlineKeyboardMarkup(row_width=1)

        if str(category) in "12":  # Отображаем курсы
            await self.print_list_courses(markup, courses, category, current_level, offset)

            if str(category) == "1":
                if end_list is False:
                    markup.row(  # Кнопка еще
                        InlineKeyboardButton(
                            text="Ещё курсы ->",
                            callback_data=self.make_callback_data(level=current_level, category=1,
                                                                  offset=(int(offset) + 5))
                        )
                    )
                print("ioff - ", offset)
                if offset != "0":
                    markup.row(  # Кнопка предыдущие
                        InlineKeyboardButton(
                            text="<- Предыдущие",
                            callback_data=self.make_callback_data(level=current_level, category=1,
                                                                  offset=(int(offset) - 5))
                        )
                    )

        else:  # Вкладка о себе
            markup.row(
                InlineKeyboardButton(
                    text="Изменить" if not empty_info else "Заполнить",
                    callback_data=self.make_callback_data(level=current_level + 1, category=category)
                )
            )

        markup.row(  # Кнопка возвращения на уровень ниже для любого случая
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1)
            )
        )

        return markup

    # Клавиатура для уровня 2 - выбранный открытый курс
    async def item_info(self, category, item_id, is_sub, offset=0):
        current_level = 2
        markup = InlineKeyboardMarkup(row_width=1)
        print("2-", is_sub)
        markup.row(
            InlineKeyboardButton(
                text="Отменить запись" if is_sub else "Записаться",
                callback_data=self.make_callback_data(level=current_level + 1, category=category, item_id=item_id,
                                                      is_sub=is_sub, offset=offset)
            )
        )
        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, category=category, offset=offset)
            )
        )

        return markup
