from aiogram.dispatcher.filters.state import StatesGroup, State


class Bonus(StatesGroup):
    """Стейты для бонусного заказа"""
    Count = State()
    WaitSeller = State()
