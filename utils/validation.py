class Validation:
    dict = {  # Цифры - номер поля
        "digit": "34",
        "text": "1256",
        "bool": "7"
    }

    def digit(self, amount):
        if not str(amount).replace('.', '').isdigit() or str(amount)[0] in "0,.":
            return "Значение должно быть числом!"
        return 200

    def text(self, text):
        if text.replace('.', '').isdigit():
            return "Значение не должно быть числом!"
        return 200

    def bool(self, text):
        if int(text) == 1 or int(text) == 0:
            return 200
        return "Значение должно быть 1 или 0!"

    def validate(self, message, m_type):
        if m_type in self.dict['digit']:
            return self.digit(message)
        elif m_type in self.dict['text']:
            return self.text(message)
        elif m_type in self.dict['bool']:
            return self.bool(message)
        else:
            raise Exception("Не знаю такого пункта")
