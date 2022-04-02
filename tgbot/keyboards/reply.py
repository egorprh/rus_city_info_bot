from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_search_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Получить информацию о городе')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

yes_no_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Да'),
            KeyboardButton(text='Нет')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

support = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Сообщить об ошибке')
        ]
    ],
    resize_keyboard=True
)
