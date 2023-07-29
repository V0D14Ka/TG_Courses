from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


class InlineAdmin:
    """
        Класс отображения клавиатур админа
    """
    menu_cd = CallbackData("show_menu", "is_admin", "level", "category", "item_id", "to_change", "flag", "offset")
    update_course_cd = CallbackData("sub", "item_id")

    def make_callback_data(self, level, is_admin=1, category=0, item_id=0, to_change=0, flag=0, offset=0):
        """
            Создание callback меню админа
        """
        return self.menu_cd.new(is_admin=is_admin, level=level, category=category, item_id=item_id, to_change=to_change,
                                flag=flag, offset=offset)

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

    async def menu_keyboard(self):
        """
            Клавиатура админа уровень 0
        """

        current_level = 0
        markup = InlineKeyboardMarkup()

        markup.insert(
            InlineKeyboardButton(text="Открытые курсы", callback_data=self.make_callback_data(
                level=current_level + 1,
                category=1))
        )

        markup.insert(
            InlineKeyboardButton(text="Закрытые курсы", callback_data=self.make_callback_data(
                level=current_level + 1,
                category=0))
        )
        return markup

    # Уровень 1
    async def category_keyboard(self, category, courses, offset=0,
                                end_list=False):
        """
            Клавиатура админа уровень 1
        """
        current_level = 1
        markup = InlineKeyboardMarkup(row_width=1)
        await self.print_list_courses(markup, courses, category, current_level, offset)

        if end_list is False:
            markup.row(  # Кнопка еще
                InlineKeyboardButton(
                    text="Ещё курсы ->",
                    callback_data=self.make_callback_data(level=current_level, category=category,
                                                          offset=(int(offset) + 5))
                )
            )

        if offset != "0":
            markup.row(  # Кнопка предыдущие
                InlineKeyboardButton(
                    text="<- Предыдущие",
                    callback_data=self.make_callback_data(level=current_level, category=category,
                                                          offset=(int(offset) - 5))
                )
            )

        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1)
            )
        )

        return markup

    async def item_info(self, category, item_id, offset=0):
        """
            Клавиатура админа уровень 2
        """
        current_level = 2
        markup = InlineKeyboardMarkup(row_width=1)

        markup.row(
            InlineKeyboardButton(
                text="Редактировать",
                callback_data=self.make_callback_data(level=current_level + 1, category=category, item_id=item_id,
                                                      offset=offset)
            )
        )
        markup.row(
            InlineKeyboardButton(
                text="Записавшиеся",
                callback_data=self.make_callback_data(level=current_level + 1, category=category, item_id=item_id,
                                                      flag=1, offset=offset)
            )
        )
        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, category=category, offset=offset)
            )
        )

        return markup

    async def update_item_menu(self, category, item_id, offset):
        """
            Клавиатура админа уровень 3 (Выбор поля для редактирования курса)
        """
        current_level = 3
        markup = InlineKeyboardMarkup(row_width=1)

        markup.row(
            InlineKeyboardButton(
                text="Название",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=1, offset=offset)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Расписание",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=2, offset=offset)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Цена",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=3, offset=offset)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Аудитория",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=4, offset=offset)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Преподаватель",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=5, offset=offset)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Комментарий",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=6, offset=offset)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Статус",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=7, offset=offset)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, item_id=item_id, category=category,
                                                      offset=offset)
            )
        )
        return markup

    async def back_markup(self, category, item_id, offset):
        """
            Клавиатура админа уровень 3 (записавшиеся)
        """
        current_level = 3
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, item_id=item_id, category=category,
                                                      offset=offset)
            )
        )
        return markup
