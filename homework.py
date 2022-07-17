import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 5
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
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
        raise telegram.TelegramError


def get_api_answer(current_timestamp):
    """Функция получения ответа от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params=params)
        logger.info('Запрос к API отправлен.')
    except telegram.TelegramError as error:
        raise telegram.TelegramError(f'Ошибка в API:{error}')
    else:
        if response.status_code != HTTPStatus.OK:
            status = response.status_code
            raise exceptions.ConnectionError(
                f'Сбой в работе программы: Эндпоинт {response}.'
                f'Недоступен. Код ответа: {status}')
    response = response.json()
    return response


def check_response(response):
    """Функция проверки данных от API.

    Формирование словаря с последней домашкой.
    """
    if not isinstance(response, dict):
        raise TypeError('API возвращает не словарь.')
    if not 'homeworks':
        raise KeyError('Отсутствует ключ homeworks.')
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        raise TypeError('Ключ homework - не список.')
    return homework


def parse_status(homework):
    """Проверка словаря с последней домашкой и формирование сообщения."""
    if not 'homework_name' and 'status':
        raise KeyError('Нет ключей в json.')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_VERDICTS[homework_status]
    if homework_status not in HOMEWORK_VERDICTS:
        raise telegram.TelegramError(
            'Отсутствие статуса домашней работы в списке.')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка получаемых токенов."""
    return all([TELEGRAM_CHAT_ID, PRACTICUM_TOKEN, TELEGRAM_TOKEN])


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if check_tokens() is False:
        raise exceptions.CriticalException('Проверка токенов провалена.')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework = homeworks[0]
                message = parse_status(homework)
                send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)
    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    main()
