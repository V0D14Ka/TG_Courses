from datetime import datetime

from DB.models import Courses


async def sort_strings_by_datetime(strings):
    """
        Сортирует массив строк расписания по возрастанию

        :param strings: Массив строк расписания

        :return: Строка расписания с разделителем ";"
    """
    def extract_datetime(string):
        date_str, time_str = string.split(' ')
        start_time_str, end_time_str = time_str.split('-')
        start_datetime_str = f"{date_str} {start_time_str}"
        end_datetime_str = f"{date_str} {end_time_str}"
        return datetime.strptime(start_datetime_str, "%d.%m.%Y %H:%M"), datetime.strptime(end_datetime_str,
                                                                                          "%d.%m.%Y %H:%M")

    sorted_strings = sorted(strings, key=lambda x: extract_datetime(x)[0])
    return ";".join(sorted_strings)


def convert_string_to_datetime(date_str):
    """
        Конвертирует дату в формате строки в тип данных datetime

        :param date_str: Дата в формате строки

        :return: Datetime
    """
    datetime_format = "%d.%m.%Y %H:%M"
    return datetime.strptime(date_str, datetime_format)


async def check_time(instance: Courses):
    """
        Проверка на необходимость создания задания на оповещение за день до начала курса.

        :param instance: Объект Courses.

        :return: Кол-во секунд до даты начала курса - 24 часа или -1 если осталось меньше дня до начала.
    """
    if instance.status is True and instance.schedule is not None:
        schedule = instance.schedule.split(";")[0][0:16]
        date = convert_string_to_datetime(schedule)
        date_now = datetime.now()

        # Если до старта курса больше дня, отправляем задание
        if date > date_now:
            sec = (date - date_now).total_seconds()
            if sec >= 86400:
                return sec - 86400

    return -1
