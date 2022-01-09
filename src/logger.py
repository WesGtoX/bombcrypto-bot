import sys
import yaml

from src.date import date_formatted


stream = open('./config.yaml', 'r')
c = yaml.safe_load(stream)

last_log_is_progress = False

COLOR = {
    'blue': '\033[94m',
    'default': '\033[99m',
    'grey': '\033[90m',
    'yellow': '\033[93m',
    'black': '\033[90m',
    'cyan': '\033[96m',
    'green': '\033[92m',
    'magenta': '\033[95m',
    'white': '\033[97m',
    'red': '\033[91m'
}


def logger(message, progress_indicator=False, color='default', line_break=''):
    global last_log_is_progress
    color_formatted = COLOR.get(color.lower(), COLOR['default'])

    formatted_datetime = date_formatted()
    formatted_message = f'{line_break}[{formatted_datetime}] => {message}'
    formatted_message_colored = color_formatted + formatted_message + '\033[0m'

    # Start progress indicator and append dots to in subsequent progress calls
    if progress_indicator:
        if not last_log_is_progress:
            last_log_is_progress = True
            formatted_message = f'{color_formatted}[{formatted_datetime}] => ⬆️ Processing last action..'
            sys.stdout.write(formatted_message)
            sys.stdout.flush()
        else:
            sys.stdout.write(color_formatted + '.')
            sys.stdout.flush()

        return

    if last_log_is_progress:
        sys.stdout.write('\n')
        sys.stdout.flush()
        last_log_is_progress = False

    print(formatted_message_colored)

    if c['save_log_to_file'] is True:
        logger_file = open('./logs/logger.log', 'a', encoding='utf-8')
        logger_file.write(f'{formatted_message}\n')
        logger_file.close()

    return True


def logger_map_clicked(window_name=''):
    logger('🗺️ New Map button clicked!')

    logger_file = open('./logs/new-map.log', 'a', encoding='utf-8')
    logger_file.write(f'[{date_formatted()}] => {window_name}\n')
    logger_file.close()
