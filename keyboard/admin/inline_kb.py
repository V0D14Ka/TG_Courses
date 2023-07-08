from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


class InlineAdmin:
    menu_cd = CallbackData("show_menu", "is_admin", "level", "category", "item_id", "to_change", "flag")
    update_course_cd = CallbackData("sub", "item_id")

    def make_callback_data(self, level, is_admin=1, category=0, item_id=0, to_change=0, flag=0):
        return self.menu_cd.new(is_admin=is_admin, level=level, category=category, item_id=item_id, to_change=to_change,
                                flag=flag)

    async def menu_keyboard(self):
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

    async def category_keyboard(self, category, courses):
        current_level = 1
        markup = InlineKeyboardMarkup(row_width=1)
        for course in courses:
            button_text = f"{course.title}"
            callback_data = self.make_callback_data(category=category, level=current_level + 1,
                                                    item_id=course.id)

            markup.insert(
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            )

        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1)
            )
        )

        return markup

    async def item_info(self, category, item_id):
        current_level = 2
        markup = InlineKeyboardMarkup(row_width=1)

        markup.row(
            InlineKeyboardButton(
                text="Редактировать",
                callback_data=self.make_callback_data(level=current_level + 1, category=category, item_id=item_id)
            )
        )
        markup.row(
            InlineKeyboardButton(
                text="Записавшиеся",
                callback_data=self.make_callback_data(level=current_level + 1, category=category, item_id=item_id,
                                                      flag=1)
            )
        )
        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, category=category)
            )
        )

        return markup

    async def back_markup(self, category, item_id):
        current_level = 3
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, item_id=item_id, category=category,
                                                      )
            )
        )
        return markup

    async def update_item_menu(self, category, item_id):
        current_level = 3
        markup = InlineKeyboardMarkup(row_width=1)

        markup.row(
            InlineKeyboardButton(
                text="Название",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=1)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Расписание",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=2)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Цена",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=3)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Аудитория",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=4)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Преподаватель",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=5)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Комментарий",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=6)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Статус",
                callback_data=self.make_callback_data(level=current_level + 1, item_id=item_id, category=category,
                                                      to_change=7)
            )
        )

        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, item_id=item_id, category=category)
            )
        )
        return markup
