from aiogram.dispatcher.filters.state import StatesGroup, State


class ProfileState(StatesGroup):
    """Стейты для изменения данных пользователя"""
    WaitMetro = State()
    WaitLocation = State()
    WaitAddress = State()