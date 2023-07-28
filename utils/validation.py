import re


# Простая самописная валидация
class Validation:
    async def val_digit(self, amount):
        if not str(amount).replace('.', '').isdigit() or str(amount)[0] in "0,.-":
            return "Значение должно быть положительным числом!"
        if len(amount) > 10:
            return "Слишком длинное число"
        return 200

    async def val_text(self, text):
        if text.replace('.', '').isdigit():
            return "Значение не должно быть числом!"
        if len(text) > 30:
            return "Слишком большой текст"
        pattern = re.compile("^[а-яА-ЯёЁa-zA-Z]+$")  # pattern
        return 200 if re.fullmatch(pattern, text.replace(' ', '')) else "Неверный формат"

    async def val_bool(self, text):
        if int(text) == 1 or int(text) == 0:
            return 200
        return "Значение должно быть 1 или 0!"

    async def val_fio(self, text):
        if len(text) > 70:
            return "Слишком большой ввод"
        pattern = re.compile("^[а-яА-ЯёЁa-zA-Z]+ [а-яА-ЯёЁa-zA-Z]+ [а-яА-ЯёЁa-zA-Z]+$")  # pattern
        return 200 if re.fullmatch(pattern, text) else "Неверный формат ввода ФИО"

    async def val_date(self, string):
        pattern = re.compile("(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])")  # pattern
        return 200 if re.fullmatch(pattern, string) else "Неверный формат ввода даты"

    async def val_mix(self, string):
        if len(string) > 70:
            return "Слишком длинное значение"
        return 200

    async def val_phone(self, string):
        pattern = re.compile("^\d{11}$")  # pattern
        return 200 if re.fullmatch(pattern, string) else "Неверный формат номера"

    async def val_passSeries(self, string):
        pattern = re.compile("^\d{4}$")  # pattern
        return 200 if re.fullmatch(pattern, string.replace(' ', '')) else "Неверный формат"

    async def val_passnumber(self, string):
        pattern = re.compile("^\d{6}$")  # pattern
        return 200 if re.fullmatch(pattern, string.replace(' ', '')) else "Неверный формат"

    async def val_passcode(self, string):
        pattern = re.compile("^\d{3}?[-]\d{3}$")  # pattern
        return 200 if re.fullmatch(pattern, string) else "Неверный формат кода"

    async def val_schedule(self, string):
        pattern = re.compile(
            "(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.]((19|20)\d\d)\s(0[1-9]|1[0-9]|2[0-4])[:]([0-5][0-9])"
            "[-](0[1-9]|1[0-9]|2[0-4])[:]([0-5][0-9])")  # pattern
        str = string.split(";")
        for i in str:
            if not re.fullmatch(pattern, i):
                return "Неверный формат расписания"

        return 200
