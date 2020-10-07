from aiogram.dispatcher.filters.state import StatesGroup, State


class SelectCourier(StatesGroup):
    """Стейты для выбора курьера"""
    WaitCourier = State()
    WaitReason = State()

    WaitReasonActive = State()
    WaitReasonCourier = State()