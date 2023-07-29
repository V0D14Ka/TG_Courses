from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


class InlineStudent:
    """
        Класс отображения клавиатур студента
    """
    menu_cd = CallbackData("student_menu", "level", "category", "item_id", "sub", "offset", "change")
    sub_course_cd = CallbackData("sub", "item_id")

    def make_callback_data(self, level, category=0, item_id=0, is_sub=0, offset=0, change=0):
        """
            Создание callback меню студента
        """
        return self.menu_cd.new(level=level, category=category, item_id=item_id, sub=is_sub, offset=offset, change=change)

    async def menu_keyboard(self):
        """
            Клавиатура студента уровень 0
        """
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

    async def print_list_courses(self, markup, courses, category, current_level, offset=0):
        """
            Функция отрисовки кнопок в клавиатуру - курсов
        """
        for course in courses:
            print(course.title)
            button_text = f"{course.title}"
            callback_data = self.make_callback_data(category=category, level=current_level + 1,
                                                    item_id=course.id, offset=int(offset))

            markup.insert(
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            )

    async def category_keyboard(self, category=0, courses=None, user_info=None, empty_info=False, offset=0,
                                end_list=False):
        """
            Клавиатура студента уровень 1
        """
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

    async def item_info(self, category, item_id, is_sub, offset=0):
        """
            Клавиатура студента уровень 2 - выбранный открытый курс
        """
        current_level = 2
        markup = InlineKeyboardMarkup(row_width=1)
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

    async def update_user_info(self, category, item_id):
        """
            Клавиатура студента уровень 2 - редактирование личных данных
        """
        current_level = 2
        markup = InlineKeyboardMarkup(row_width=1)

        markup.row(
            InlineKeyboardButton(
                text="ФИО",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=1)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Группа",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=2)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Номер телефона",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=3)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Дата рождения",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=4)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Серия паспорта",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=5)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Номер паспорта",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=6)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Дата выдачи паспорта",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=7)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Кем выдан паспорт",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=8)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Место регистрации",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=9)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Код подразделения",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      change=10)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, item_id=item_id, category=category)
            )
        )
        return markup
