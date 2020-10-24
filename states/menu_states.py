from aiogram.dispatcher.filters.state import StatesGroup, State


class SignUpUser(StatesGroup):
    """Стейты для выбора адреса доставки при старте"""
    Metro = State()
    Location = State()


class Menu(StatesGroup):
    """Стейты для заказа"""
    WaitCategory = State()

    WaitProduct = State()

    WaitProductSize = State()

    WaitProductSizeBack = State()

    WaitQuantity = State()
    WaitQuantity6 = State()

    WaitQuantityFromSize = State()

    OneMoreOrNext = State()

    WaitQuantityBack = State()
    WaitQuantity6Back = State()

    WaitQuantityBackWithSizeId = State()
    WaitQuantity6BackWithSize = State()
    WaitQuantity6BackWithSizeId = State()

    # WaitQuantity6FromSize = State()

    WaitQuantityBackWithSize = State()

    WaitAddress = State()
    WaitNewAddress = State()
    WaitPass = State()
    WaitTime = State()

    WaitUserConfirmationPickup = State()
    WaitUserConfirmationDelivery = State()

    OrderStatus = State()
    WaitReasonUser = State()

    WaitReview = State()

    BonusOrderStatus = State()
    WaitBonusReview = State()
