from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


class InlineAdmin:
    menu_cd = CallbackData("show_menu", "is_admin", "level", "category", "item_id")
    sub_course_cd = CallbackData("sub", "item_id")

    def __init__(self, db):
        self.db = db

    def make_callback_data(self, is_admin, level, category=0, item_id=0):
        return self.menu_cd.new(is_admin=is_admin, level=level, category=category, item_id=item_id)

    async def menu_keyboard(self, is_admin):
        current_level = 0
        markup = InlineKeyboardMarkup()

        markup.insert(
            InlineKeyboardButton(text="Открытые курсы", callback_data=self.make_callback_data(is_admin=is_admin,
                                                                                              level=current_level + 1,
                                                                                              category=1))
        )

        markup.insert(
            InlineKeyboardButton(text="Закрытые курсы", callback_data=self.make_callback_data(is_admin=is_admin,
                                                                                              level=current_level + 1,
                                                                                              category=2))
        )
        return markup

    async def category_keyboard(self, is_admin, category):
        current_level = 1
        markup = InlineKeyboardMarkup(row_width=1)
        print(category)
        courses = self.db.get_courses(category)
        for course in courses:
            print(course[1])
            button_text = f"{course[1]}"
            callback_data = self.make_callback_data(is_admin=is_admin, category=category, level=current_level + 1,
                                                    item_id=course[0])

            markup.insert(
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            )

        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, is_admin=is_admin)
            )
        )

        return markup

    async def item_info(self, is_admin, category, item_id):
        current_level = 2
        markup = InlineKeyboardMarkup(row_width=1)
        item = self.db.get_course(item_id)

        markup.row(
            InlineKeyboardButton(  # TODO пока заглушка
                text="Редактировать",
                callback_data=self.make_callback_data(level=current_level - 1, is_admin=is_admin, category=category)
            )
        )
        markup.row(
            InlineKeyboardButton(  # TODO пока заглушка
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, is_admin=is_admin, category=category)
            )
        )

        return markup
