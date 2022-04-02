from aiogram.dispatcher.filters.state import StatesGroup, State


class choseCityStates(StatesGroup):
    give_city_name = State()
    confirm_city = State()
