import os
import time

import requests
import telegram
from dotenv import load_dotenv
from requests import RequestException

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    hw_status = homework.get('status')
    if homework_name is None:
        return 'Данные из API не получены.'
    if hw_status is None:
        return 'Данные из API не получены.'
    if hw_status != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):

    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    from_date = current_timestamp
    params = {'from_date': from_date}
    try:
        request = requests.get(
            f'https://praktikum.yandex.ru/api/user_api/homework_statuses/?from_daate={from_date}',
            headers=headers, params=params).json()
    except RequestException as e:
        return f'В функции get_homework_statuses обнаружена ошибка {e}'
    return request



def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot)
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            if current_timestamp is None:
                current_timestamp = int(time.time())
            # обновить timestamp
            time.sleep(1600)  # опрашивать раз в 20 минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
