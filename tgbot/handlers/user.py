import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.misc.sqliteapi import Database
from tgbot.states.chosecity import choseCityStates


async def user_start(message: Message):
    user = message.from_user

    db: Database = message.bot.get("db")

    db.insert_record('users', telegram_id=user.id, first_name=user.first_name, username=user.username,
                     language_code=user.language_code)

    await message.answer("Hello, user! Give me city name")
    await choseCityStates.give_city_name.set()


async def get_city_name(message: Message, state: FSMContext):
    user_message = message.text

    # Если есть города в стейте то берем их
    # Если в стейте пусто и стейт пользователя говорит о том что он дал название города,
    # то берем города из базы
    results = await state.get_data()
    results = results.get('cities')
    user_state = await state.get_state()
    if not results and user_state == 'choseCityStates:give_city_name':
        city_name = user_message.lower()
        db: Database = message.bot.get("db")
        results = db.get_records_sql("SELECT * FROM cities WHERE address LIKE ?", '%' + city_name)

    # Если городов нет, то сообщаем об этом
    if len(results) == 0:
        await message.answer('Ничего не найдено. Проверьте город на опечатки. Или введите близжайший крупный город')
        await choseCityStates.give_city_name.set()
    else:
        # Берем первый город
        city = results.pop(0)
        # Сетим оставшиеся города в стейт
        await state.update_data(cities=results)
        # Сетим выбранный город в стейт
        await state.update_data(city=city)

        # Если в массиве городов ничего не осталось, то сразу выдаем результатов
        if not results:
            await give_result(message, state)
        else:
            await message.answer(f"Это ваш город? {city.get('city')} {city.get('region')} {city}")
            await choseCityStates.confirm_city.set()


async def confirm_city(message: Message, state: FSMContext):
    user_message = message.text

    # Если город его, то выдаем информацию о нем
    if user_message == 'Да':
        await give_result(message, state)
    # Если город не его, то возвращаем назад
    elif user_message == 'Нет':
        await get_city_name(message, state)
    else:
        await message.answer('Ответь Да или Нет')


async def give_result(message: Message, state: FSMContext):
    result = await state.get_data()
    result: dict = result.get('city')
    dbtz = result.get('timezone')
    offset = datetime.timedelta(hours=int(dbtz.replace('UTC', '')))
    tz = datetime.timezone(offset, dbtz)
    current_time = datetime.datetime.now(tz)
    local_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    year = current_time.year
    timestamp = current_time.timestamp()

    await message.answer(f"""
            {result.get('city')}, {result.get('region')}
            Почтовый индекс: {result.get('postal_code')}
            Округ: {result.get('district')}
            Регион: {result.get('region')}
            Часовой пояс: {result.get('timezone')}
            Местное время: {local_time}
            Timestamp: {timestamp}
            Население (на 2021 год): {result.get('population')} 
            Год основания: {result.get('foundation_year')}
            Возраст города: {year - int(result.get('foundation_year'))}
            latitude: {result.get('geo_lat')}
            longitude: {result.get('geo_lon')}
            """)
    await message.bot.send_location(message.chat.id, latitude=result.get('geo_lat'),
                                    longitude=result.get('geo_lon'))

    # очищаем данные и устанавливаем начальный стейт
    await state.reset_data()
    await choseCityStates.give_city_name.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(get_city_name, state=choseCityStates.give_city_name)
    dp.register_message_handler(confirm_city, state=choseCityStates.confirm_city)
