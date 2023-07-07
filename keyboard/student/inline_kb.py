from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


class InlineStudent:
    menu_cd = CallbackData("show_menu", "level", "category", "item_id")
    sub_course_cd = CallbackData("sub", "item_id")

    # Создаем колбек дату
    def make_callback_data(self, level, category=0, item_id=0):
        return self.menu_cd.new(level=level, category=category, item_id=item_id)

    # Универсальная клавиатура для уровня 1
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

    # Универсальная клавиатура для уровня 2
    async def category_keyboard(self, category=0, courses=None, user_info=None, empty_info=False):
        current_level = 1
        markup = InlineKeyboardMarkup(row_width=1)
        print(category)

        # Делаем клавиатуру по выбранной категории меню
        match category:
            case "1":  # Рисуем кнопки с курсами, проверяем courses
                for course in courses:
                    print(course[1])
                    button_text = f"{course[1]}"
                    callback_data = self.make_callback_data(category=category, level=current_level + 1,
                                                            item_id=course[0])

                    markup.insert(
                        InlineKeyboardButton(text=button_text, callback_data=callback_data)
                    )
            case "2":  # Рисуем кнопки с курсами на которые записался студент, проверяем user_info
                print("Выбраны мои курсы")  # TODO пока заглушка
                pass

            case "3":  # Кнопки вкладки о себе, проверяем empty_info
                markup = InlineKeyboardMarkup(row_width=1)

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

    # Клавиатура для уровня 3 - выбранный открытый курс
    async def item_info(self, category, item_id):
        current_level = 2
        markup = InlineKeyboardMarkup(row_width=1)

        markup.row(
            InlineKeyboardButton(
                text="Записаться",
                callback_data=self.make_callback_data(level=current_level - 1, category=category)
            )
        )
        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=self.make_callback_data(level=current_level - 1, category=category)
            )
        )

        return markup
