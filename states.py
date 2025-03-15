from aiogram.dispatcher.filters.state import State, StatesGroup


# Все состояния
class States(StatesGroup):
    change = State()
    mailing = State()
