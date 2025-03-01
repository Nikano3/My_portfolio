import json

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F, Router
from app.main_file import Browser

router = Router()


class Handlers:
    @router.message(F.text.lower().strip('') == "квартиры")
    async def get_appartaments(self: Message):
        await self.answer('Подождите, операция выполняется...')
        parser = Browser()
        try:
            # Получаем результаты парсинга
            results = await parser.main()
            results = [item for sublist in results for item in sublist]
            url = results[0].get("Ссылка")
            # results = results[0].pop['Ссылка']
            print('АУУУУУУУУУУ', url)
            if results:
                while results:
                    formatted_data = "\n".join([f"{key}: {value}" for key, value in results[0].items()])
                    buttons = []
                    button = [InlineKeyboardButton(text='Посмотреть', url=url)]
                    buttons.append(button)
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    await self.answer(formatted_data, reply_markup=keyboard)
                    del results[0]

            else:
                await self.answer('Нет новых объявлений')

        except Exception as e:
            # Логирование ошибки
            print(f"Ошибка при парсинге: {e}")
            await self.answer('Произошла ошибка при получении данных.')
