import json
import os
import random
import logging  # Подключаем модуль для логирования

import pytz
from telethon import TelegramClient
from datetime import datetime, timedelta
import asyncio

# Настройка логгера
logger = logging.getLogger()

# Устанавливаем уровень логирования (INFO — информационные сообщения)
logger.setLevel(logging.INFO)

# Формат вывода логов
log_format = '%(asctime)s - %(levelname)s - %(message)s'

# Обработчик для записи логов в файл
file_handler = logging.FileHandler('log/parse_tg.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)  # Уровень логирования для файла
file_handler.setFormatter(logging.Formatter(log_format))

# Обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Уровень логирования для консоли
console_handler.setFormatter(logging.Formatter(log_format))

# Добавляем обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)




class Parse_tg:

    async def get_channel_messages(self, channel):

        # Устанавливаем дату 24 часа назад
        time_limit = datetime.now(pytz.utc) - timedelta(days=1)

        channel_link = channel
        logger.info(f"Получаем сообщения с канала: {channel_link}")

        try:
            messages = await self.client.get_messages(channel_link, limit=1000)  # Можно изменить лимит
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений с канала {channel_link}: {e}")
            return

        # Фильтруем по времени и исключаем пустые сообщения (None)
        recent_messages = [msg for msg in messages if msg.date >= time_limit and msg.text]

        # Удаление дубликатов по уникальному идентификатору сообщения
        unique_messages = {msg.id: msg for msg in recent_messages}.values()

        # Сохраняем сообщения
        await self.save(unique_messages, channel_link)

    async def save(self, recent_messages, channel_link):
        try:
            # Изменим режим открытия на 'a' для добавления данных в конец файла
            with open('finally_txt/messages.txt', 'a', encoding='utf-8') as file:
                for message in recent_messages:
                    msg_date = message.date.astimezone(pytz.timezone("Europe/Moscow"))
                    link = f"https://t.me/{channel_link.strip('/').split('/')[-1]}/{message.id}"

                    file.write(f"Дата: {msg_date.strftime('%Y-%m-%d')}\n\n")
                    file.write(f"Время: {msg_date.strftime('%H:%M:%S')}\n\n")
                    file.write(f"Ссылка: {link}\n\n")
                    file.write(f"Текст:\n{message.text}\n\n")
                    file.write('-' * 35 + '\n\n')

            logger.info(f"Данные добавлены в файл finally_txt/messages.txt")
        except Exception as e:
            logger.error(f"Ошибка при сохранении сообщений: {e}")

    async def make_client(self, data):
        api_id = data['api_id']
        api_hash = data['api_hash']
        self.client = TelegramClient('session_name', api_id, api_hash)

        try:
            await self.client.start()
            if await self.client.is_user_authorized():
                logger.info("Авторизация прошла успешно!")
            else:
                logger.error("Авторизация не удалась.")
                return
        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            return

    async def for_accept(self):
        messages_file = 'finally_txt/messages.txt'
        json_file = 'data_for_login/data.json'
        channels_file = 'channels/channels.txt'

        # Проверка существования файла с данными для авторизации
        if not os.path.exists(json_file):
            # Если файл не существует, запрашиваем данные у пользователя
            api_id = input('Введите свой api id: ')
            api_hash = input('Введите свой api hash: ')
            phone_number = input('Введите свой номер телефона: ')

            data = {
                'api_id': api_id,
                'api_hash': api_hash,
                'phone_number': phone_number
            }

            try:
                with open(json_file, 'w') as file:
                    json.dump(data, file)
                logger.info('Данные сохранены в файл.')
            except Exception as e:
                logger.error(f"Ошибка при сохранении данных в файл {json_file}: {e}")

        else:
            try:
                with open(json_file, 'r') as file:
                    data = json.load(file)
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {json_file}: {e}")
                return

            if not os.path.exists(channels_file):
                logger.error(f"Файл {channels_file} не найден. Создайте его с указанием каналов.")
                return

            try:
                with open(channels_file, 'r') as file:
                    channels = file.readlines()
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {channels_file}: {e}")
                return

            channels = [channel.strip() for channel in channels if channel.strip()]
            logger.info(f"Список каналов: {channels}")

            await self.make_client(data)
            number = 1
            for channel in channels:
                if number % 10 == 0 and number != 0:
                    delay = random.randint(14, 23)
                    await asyncio.sleep(delay)
                    logger.info(f"Задержка: {delay} секунд")
                    number += 1
                    await self.get_channel_messages(channel)
                else:
                    delay = random.randint(3, 5)
                    logger.info(f"Задержка: {delay} секунд -- {number}/{len(channels)}")
                    await asyncio.sleep(delay)
                    number += 1
                    await self.get_channel_messages(channel)


if __name__ == '__main__':
    path = 'finally_txt/messages.txt'
    if os.path.exists(path):
        os.remove(path)
    a = Parse_tg()
    asyncio.run(a.for_accept())
