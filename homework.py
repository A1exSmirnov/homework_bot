
import sys
import time
import logging
import requests
from http import HTTPStatus

from telegram import Bot

from config import (
    PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
    RETRY_TIME, ENDPOINT, HEADERS, HOMEWORK_STATUSES
)
from exceptions import (
    error_message, new_status, EndpointUrl, HomeworkNewStatus,
    DictIsNotEmpty, ResponseNotList
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Функция делает запрос отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Сбой при отправке сообщения: {error}', exc_info=True)
    else:
        logger.info(f'Сообщение отправлено: {message}')


def get_api_answer(current_timestamp):
    """
    Функция делает запрос к API Практикум.Домашка.
    И возвращает ответ API, преобразовав его из формата JSON
    к типам данных Python.
    """
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    status_code = homework_statuses.status_code
    if status_code != HTTPStatus.OK:
        raise EndpointUrl(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {status_code}'
        )
    response = homework_statuses.json()
    return response


def check_response(response):
    """
    Функция проверяет ответ API на корректность.
    И если ответ API соответствует ожиданиям,
    возвращает список домашних работ.
    """
    if type(response) is not dict:
        raise TypeError('Ответ от API имеет некорректный тип')
    if not response:
        raise DictIsNotEmpty('Ответ от API содержит пустой словарь')
    homeworks = response.get('homeworks')
    if type(homeworks) is not list:
        raise ResponseNotList(
            'Под ключом "homeworks",'
            'домашки приходят не в виде списка'
        )
    return homeworks


def parse_status(homework):
    """
    Функция извлекает из информации о домашней работе статус этой работы.
    Проверка наличия необходимых ключей
    в словаре ответа API, под ключом "homeworks".
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise Exception('Недокументированный статус домашней работы')
    verdict = HOMEWORK_STATUSES[homework_status]
    try:
        new_status(homework_status)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except HomeworkNewStatus:
        print('Ожидание нового статуса проверки работы')
        return None


def check_tokens():
    """
    Проверка доступности переменных окружения.
    Которые необходимы для работы программы.
    """
    if PRACTICUM_TOKEN is None or not PRACTICUM_TOKEN:
        logging.critical(
            'Отсутствует обязательная переменная окружения: "PRACTICUM_TOKEN".'
            ' Программа принудительно остановлена.'
        )
        return False
    elif TELEGRAM_TOKEN is None or not TELEGRAM_TOKEN:
        logging.critical(
            'Отсутствует обязательная переменная окружения: "TELEGRAM_TOKEN".'
            ' Программа принудительно остановлена.'
        )
        return False
    elif TELEGRAM_CHAT_ID is None or not TELEGRAM_CHAT_ID:
        logging.critical(
            'Отсутствует обязательная переменная окружения: '
            '"TELEGRAM_CHAT_ID".'
            ' Программа принудительно остановлена.'
        )
        return False
    return True


def main():
    """Основная логика работы бота."""
    tokens = check_tokens()
    while tokens is True:
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            current_timestamp = 0  # int(time.time())
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks != []:
                homework = homeworks[0]
                message = parse_status(homework)
                if message is not None:
                    send_message(bot, message)
            time.sleep(RETRY_TIME)
        except Exception as error:
            logging.exception(error, exc_info=True)
            message = f'Сбой в работе программы: {error}'
            check_message = error_message(message)
            if check_message is not True:
                send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
