from http import HTTPStatus
import telegram
from dotenv import load_dotenv
import os
import requests
import time
import logging
from logging import StreamHandler
import sys


load_dotenv()


logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s')

logger.setLevel(logging.INFO)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Функция отправки сообщения."""
    try:
        logger.info(f'Бот отправил сообщение: {message}')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError:
        logger.error('Сообщение не отправлено')
        raise telegram.TelegramError


def get_api_answer(current_timestamp):
    """Функция получения ответа от API."""
    try:
        timestamp = current_timestamp or int(time.time())
        params = {'from_date': timestamp}
        result = requests.get(
            ENDPOINT, headers=HEADERS, params=params)
        if result.status_code != HTTPStatus.OK:
            status = result.status_code
            logger.error(
                f'Сбой в работе программы: Эндпоинт {result}.'
                f'Недоступен. Код ответа: {status}')
            raise telegram.error.BadRequest
    except telegram.TelegramError as error:
        logger.error(f'Ошибка с API: {error}')
        raise telegram.TelegramError(f'Ошибка в API:{error}')
    response = result.json()

    return response


def check_response(response):
    """Функция проверки данных от API.
    Формирование словаря с последней домашкой.
    """
    if type(response) != dict:
        logger.error('API возвращает не тот тип данных.')
        raise TypeError('API возвращает не тот тип данных.')
    homework = response['homeworks'][0]
    return homework


def parse_status(homework):
    """Проверка словаря с последней домашкой и формирование сообщения."""
    if 'homework_name' not in homework:
        raise KeyError('Нет ключей в json')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status not in HOMEWORK_STATUSES:
        logger.error('Отсутствие статуса домашней работы в списке.')
        raise telegram.TelegramError

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка получаемых токенов."""
    if all([TELEGRAM_CHAT_ID, PRACTICUM_TOKEN, TELEGRAM_TOKEN]):
        return True
    return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    old_message = ''
    if check_tokens() is False:
        logger.critical('Проверка токенов провалена.')
        raise telegram.error.InvalidToken('Проверка токенов провалена.')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response['current_date']
            homework = check_response(response)
            message = parse_status(homework)
            if old_message != message:
                send_message(bot, message)
                message = old_message
                time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
