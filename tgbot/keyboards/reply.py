from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import emoji

give_info = emoji.emojize(':city_sunrise: Получить информацию о городе')
yes = emoji.emojize(':white_check_mark: Да')
no = emoji.emojize(':negative_squared_cross_mark: Нет')
report_error = emoji.emojize(':shipit: Сообщить об ошибке')

start_search_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=give_info)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

yes_no_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=yes),
            KeyboardButton(text=no)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

support = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=report_error)
        ]
    ],
    resize_keyboard=True
)
