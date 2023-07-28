from datetime import datetime

from DB.models import Courses


async def sort_strings_by_datetime(strings):
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
    datetime_format = "%d.%m.%Y %H:%M"
    return datetime.strptime(date_str, datetime_format)


async def check_time(instance: Courses):
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
