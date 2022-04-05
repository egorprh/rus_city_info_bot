import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from aiogram.utils import emoji

from tgbot.misc.sqliteapi import Database
from tgbot.states.chosecity import choseCityStates
from tgbot.keyboards.reply import yes_no_button, start_search_button


async def user_start(message: Message):
    user = message.from_user

    db: Database = message.bot.get("db")

    if db.get_record('users', telegram_id=user.id):
        await message.answer(emoji.emojize(":cop: Ты уже нажимал на Start, хитрец"), reply_markup=start_search_button)
    else:
        db.insert_record('users', telegram_id=user.id, first_name=user.first_name, username=user.username,
                         language_code=user.language_code)

        await message.answer(emoji.emojize(":arrow_down: Чтобы начать поиск - нажми кнопку "
                                           "'Получить информацию о городе'"),
                             reply_markup=start_search_button)


async def start_search(message: Message):
    await message.answer(emoji.emojize(":pencil2: Введи название города о котором хочешь получить информацию"))
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
        if len(results) > 1:
            await state.update_data(several_result=True)
            await message.answer(emoji.emojize(f":satellite: Найдено {len(results)} населенных пунктов"))

    # Если городов нет, то сообщаем об этом
    if not results:
        await message.answer(emoji.emojize(':earth_asia: Я не нашел такого города. Введи полное название, '
                                           'проверь на опечатки или введи ближайший крупный населенный пункт'),
                             reply_markup=start_search_button)
        await state.reset_state(True)
    else:
        # Берем первый город
        city = results.pop(0)
        # Сетим оставшиеся города в стейт
        await state.update_data(cities=results)
        # Сетим выбранный город в стейт
        await state.update_data(city=city)

        # Если в массиве городов ничего не осталось, то сразу выдаем результатов
        if not results:
            state_data = await state.get_data()
            if state_data.get('several_result'):
                await message.answer(emoji.emojize(":sweat_smile: Тогда остался только такой вариант:"))
            await give_result(message, state)
        else:
            await message.answer(emoji.emojize(f":smirk: Нашел несколько городов, есть такой: {city.get('city')}, "
                                               f"{city.get('region')}. :house: Это твой город?"),
                                 reply_markup=yes_no_button)
            await choseCityStates.confirm_city.set()


async def confirm_city(message: Message, state: FSMContext):
    user_message = message.text

    # Если город его, то выдаем информацию о нем
    if user_message.find('Да') != -1:
        await give_result(message, state)
    # Если город не его, то возвращаем назад
    elif user_message.find('Нет') != -1:
        await get_city_name(message, state)
    else:
        await message.answer(emoji.emojize(':bow: Ну ты просто скажи "Да" или "Нет", на кнопочку нажми :point_down:'))


async def give_result(message: Message, state: FSMContext):
    result = await state.get_data()
    result: dict = result.get('city')
    # Получаем таймзону в формате UTC+N
    dbtz = result.get('timezone')
    # Считаем смещение, для этого вычищаем из строки "UTC", т.е. остается +3 или -3
    offset = datetime.timedelta(hours=int(dbtz.replace('UTC', '')))
    # Получаем таймзону
    tz = datetime.timezone(offset, dbtz)
    # Получаем время соответвующее таймзоне
    current_time = datetime.datetime.now(tz)
    # Форматируем время
    local_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
    year = current_time.year
    timestamp = current_time.timestamp()

    await message.answer(emoji.emojize(f":white_check_mark: Нашел! {result.get('city')}, {result.get('region')}\n"
                         f":postbox: Почтовый индекс: {result.get('postal_code')}\n"
                         f":station: Округ: {result.get('district')}\n"
                         f":sunrise_over_mountains: Регион: {result.get('region')}\n"
                         f":earth_asia: Часовой пояс: {result.get('timezone')}\n"
                         f":watch: Местное время: {local_time}\n"
                         f":hourglass: Timestamp: {timestamp}\n"
                         f":busts_in_silhouette: Население (на 2021 год): {result.get('population')}\n"
                         f":triangular_flag_on_post: Год основания: {result.get('foundation_year')}\n"
                         f":1234: Возраст города: {year - int(result.get('foundation_year'))}\n"
                         f":round_pushpin: Широта: {result.get('geo_lat')}\n"
                         f":round_pushpin: Долгота: {result.get('geo_lon')}"), reply_markup=start_search_button)
    await message.bot.send_location(message.chat.id, latitude=result.get('geo_lat'),
                                    longitude=result.get('geo_lon'))

    # очищаем данные и стейт
    await state.reset_state(True)


async def plug(message: Message):
    await message.answer(emoji.emojize(':sweat_smile: Извини, кроме как выдавать информацию о городах России я больше ничего не умею. '
                         'Если хочешь получить информацию о городе - жми кнопочку :point_down:'),
                         reply_markup=start_search_button)


def register_user(dp: Dispatcher):
    dp.register_message_handler(start_search, Text(contains='Получить информацию о городе'), state="*")
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(get_city_name, state=choseCityStates.give_city_name)
    dp.register_message_handler(confirm_city, state=choseCityStates.confirm_city)
    dp.register_message_handler(plug, state="*", content_types=types.ContentTypes.ANY)
