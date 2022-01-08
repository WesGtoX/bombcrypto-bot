import time


def date_formatted(date_format='%Y-%m-%d %H:%M:%S'):
    datetime = time.localtime()
    return time.strftime(date_format, datetime)
