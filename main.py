import os
import asyncio

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv



from handlers.admin_private import admin_router
from handlers.user_group import user_group_router
from handlers.user_private import user_private_router

from DataBase.engine import create_db, session_maker

from middlewares.middleware import DataBaseSession

load_dotenv(find_dotenv())


bot = Bot(token=os.getenv("token"))
Bot.my_admins_list = []

dp = Dispatcher()

dp.include_router(user_group_router)
dp.include_router(user_private_router)
dp.include_router(admin_router)





async def main():
    await create_db()

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())