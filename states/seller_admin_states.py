from aiogram.dispatcher.filters.state import StatesGroup, State


class SellerAdmin(StatesGroup):
    """Стейты для SellerAdmina"""
    SellerName = State()
    SellerTelegramID = State()

    RemoveSeller = State()

    CourierName = State()
    CourierTelegramID = State()

    RemoveCourier = State()

    RemoveCategoryFromStock = State()
    ReturnCategoryToStock =State()

    RemoveItemFromStockCategory = State()
    RemoveItemFromStockProduct = State()

    ReturnItemToStockCategory = State()
    ReturnItemToStockProduct = State()

    DeliveryCategory = State()
    DeliveryProduct = State()
    DeliveryQuantity = State()
    DeliveryQuantity6 = State()
    ConfirmTempOrder = State()
    ConfirmTempOrderRemoved = State()
    DeliveryDate = State()
    DeliveryTime = State()
    ConfirmOrder = State()

    ChangeOrder = State()

    ChangeDeliveryDate = State()
    ChangeDeliveryTime = State()
    ChangeDeliveryConfirm = State()
    ChangeDeliveryWaitConfirm = State()

    WaitCancelConfirm = State()

