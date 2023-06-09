from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


class InlineStudent:
    menu_cd = CallbackData("show_menu", "level", "category", "item_id")
    sub_course_cd = CallbackData("sub", "item_id")

    def make_callback_data(self, level, category=0, item_id=0):
        return self.menu_cd.new(level=level, category=category, item_id=item_id)

    async def menu_keyboard(self):
        current_level = 0
        markup = InlineKeyboardMarkup()

        markup.insert(
            InlineKeyboardButton(text="Открытые курсы", callback_data=self.make_callback_data(level=current_level + 1,
                                                                                              category=1))
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

    async def category_keyboard(self, category, courses):
        current_level = 1
        markup = InlineKeyboardMarkup(row_width=1)
        print(category)

        match category:
            case "1":
                for course in courses:
                    print(course[1])
                    button_text = f"{course[1]}"
                    callback_data = self.make_callback_data(category=category, level=current_level + 1,
                                                            item_id=course[0])

                    markup.insert(
                        InlineKeyboardButton(text=button_text, callback_data=callback_data)
                    )
            case "2":
                print("Выбраны мои курсы")  # TODO пока заглушка
                pass

            case "3":
                print("Выбрано обо мне")  # TODO пока заглушка
                pass

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
            InlineKeyboardButton(  # TODO пока заглушка
                text="Записаться",
                callback_data=self.make_callback_data(level=current_level - 1, category=category)
            )
        )
        markup.row(
            InlineKeyboardButton(  # TODO пока заглушка
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, category=category)
            )
        )

        return markup
