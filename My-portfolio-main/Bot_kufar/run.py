
import logging
from aiogram import Bot, Dispatcher, types
import asyncio
from config import TOKEN
from app.handlers import router
bot = Bot(token=TOKEN)
dp = Dispatcher()
async def main1():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main1())
    except KeyboardInterrupt:
        print("Exit")
