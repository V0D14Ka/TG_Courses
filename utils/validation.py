import re

from dadata import DadataAsync


class Validation:
    """
        Валидация на регулярных выражениях.
    """

    async def val_digit(self, amount):
        """
            Валидация положительное число.

            :param amount: Число.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        if not str(amount).replace('.', '').isdigit() or str(amount)[0] in "0,.-":
            return "Значение должно быть положительным числом!"
        if len(amount) > 10:
            return "Слишком длинное число"
        return 200

    async def val_text(self, text):
        """
            Валидация текста.

            :param text: Строка.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        if text.replace('.', '').isdigit():
            return "Значение не должно быть числом!"
        if len(text) > 60:
            return "Слишком большой текст"
        pattern = re.compile("^[а-яА-ЯёЁa-zA-Z]+$")  # pattern
        return 200 if re.fullmatch(pattern, text.replace(' ', '')) else "Неверный формат"

    async def val_bool(self, value):
        """
            Валидация boolean.

            :param value: Bool.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        if int(value) == 1 or int(value) == 0:
            return 200
        return "Значение должно быть 1 или 0!"

    async def val_fio(self, text):
        """
            Валидация ФИО.

            :param text: ФИО вида Иванов Иван Иванович.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        if len(text) > 70:
            return "Слишком большой ввод"
        pattern = re.compile("^[а-яА-ЯёЁa-zA-Z]+ [а-яА-ЯёЁa-zA-Z]+ ?[а-яА-ЯёЁa-zA-Z]+$")  # pattern
        return 200 if re.fullmatch(pattern, text) else "Неверный формат ввода ФИО"

    async def val_date(self, string):
        """
            Валидация даты.

            :param string: Дата в формате строки YYYY-MM-DD.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        pattern = re.compile("(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])")  # pattern
        return 200 if re.fullmatch(pattern, string) else "Неверный формат ввода даты"

    async def val_mix(self, string):
        """
            Валидация смеси текст + числа.

            :param string: Строка.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        if len(string) > 70:
            return "Слишком длинное значение"
        return 200

    async def val_phone(self, string):
        """
            Валидация номера телефона.

            :param string: Строка с телефоном 89141112233.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        pattern = re.compile("^\d{11}$")  # pattern
        return 200 if re.fullmatch(pattern, string) else "Неверный формат номера"

    async def val_passSeries(self, string):
        """
            Валидация серии паспорта.

            :param string: Строка с числом длины 4.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        pattern = re.compile("^\d{4}$")  # pattern
        return 200 if re.fullmatch(pattern, string.replace(' ', '')) else "Неверный формат"

    async def val_passnumber(self, string):
        """
            Валидация номера паспорта.

            :param string: Строка с числом длины 6.

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        pattern = re.compile("^\d{6}$")  # pattern
        return 200 if re.fullmatch(pattern, string.replace(' ', '')) else "Неверный формат"

    async def val_passcode(self, string):
        """
            Валидация кода подразделения паспорта.

            :param string: Строка с числом длины 3-3 (111-222).

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        pattern = re.compile("^\d{3}?[-]\d{3}$")  # pattern
        return 200 if re.fullmatch(pattern, string) else "Неверный формат кода"

    async def val_schedule(self, string):
        """
            Валидация расписания.

            :param string: Строка с расписанием с разделителем ";".

            :return: 200 если все хорошо, иначе строку с ошибкой.
        """
        pattern = re.compile(
            "(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.]((19|20)\d\d)\s(0[1-9]|1[0-9]|2[0-4])[:]([0-5][0-9])"
            "[-](0[1-9]|1[0-9]|2[0-4])[:]([0-5][0-9])")  # pattern
        str = string.split(";")
        for i in str:
            if not re.fullmatch(pattern, i):
                return "Неверный формат расписания"

        return 200

    async def val_address(self, new_value, DADATA_TOKEN, DADATA_SECRET):
        """
        Валидация адреса с помощью сервиса DaData.
        :param new_value: Строка с адресом.
        :param DADATA_TOKEN: Токен сервиса.
        :param DADATA_SECRET: Токен сервиса.
        :return: Код проверки, пример правильного заполнения, отформатированная строка с адресом.
        """
        # Потом добавлю конкретную ошибку во вводе
        async with DadataAsync(DADATA_TOKEN, DADATA_SECRET) as dadata:
            ans = await dadata.clean(name="address", source=new_value)

        code, example = 0, ""

        match ans["qc"]:
            case 0:
                code = 200
                example = "'Приморский край, г.Владивосток, ул. Гоголя 17 кв 5'"
            case 1:
                code = "Заведомо неверный адрес"
                example = "'Приморский край, г.Владивосток, ул. Гоголя 17 кв 5'"
            case 2:
                code = "В адресе присутствуют лишние части"
                example = "'Приморский край, г.Владивосток, ул. Гоголя 17 кв 5'"
            case 3:
                code = "Существует несколько вариантов данного адреса, уточните"
                example = "'Приморский край, г.Владивосток, ул. Гоголя 17 кв 5'"

        return code, example, ans["result"]
