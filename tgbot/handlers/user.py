import datetime

from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.misc.sqliteapi import Database


async def user_start(message: Message):
    await message.reply("Hello, user! Give me city name")


async def get_city_name(message: Message):
    city_name = message.text
    db: Database = message.bot.get("db")

    results = db.get_records_sql(f"SELECT * FROM cities WHERE address LIKE '%{city_name}'")

    if len(results) == 0:
        await message.answer('Ничего не найдено. Проверьте город на опечатки.')

    for result in results:

        dbtz = result.get('timezone')
        offset = datetime.timedelta(hours=int(dbtz.replace('UTC', '')))
        tz = datetime.timezone(offset, dbtz)
        current_time = datetime.datetime.now(tz)
        local_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        year = current_time.year
        timestamp = current_time.timestamp()

        await message.answer(f"""
        {result.get('address')}
        Почтовый индекс: {result.get('postal_code')}
        Округ: {result.get('district')}
        Регион: {result.get('region')}
        Часовой пояс: {result.get('timezone')}
        Местное время: {local_time}
        Timestamp: {timestamp}
        Население (На какой год?): {result.get('population')} 
        Год основания: {result.get('foundation_year')}
        Возраст города: {year - int(result.get('foundation_year'))}
        """)
        await message.bot.send_location(message.chat.id, latitude=result.get('geo_lat'), longitude=result.get('geo_lon'))


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(get_city_name, state="*")
