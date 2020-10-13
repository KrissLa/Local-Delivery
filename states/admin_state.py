from aiogram.dispatcher.filters.state import StatesGroup, State


class AddAdmin(StatesGroup):
    """Стейты для бонусного заказа"""
    BanID = State()
    UnBanID = State()
    BanReason = State()

    PromoPhoto = State()
    PromoCaption = State()
    PromoConfirm = State()

    SetAbout = State()

    WaitName = State()
    WaitId = State()

    WaitDeleteAdmins = State()

    WaitMetroName = State()

    WaitDeleteMetro = State()

    NewLocationMetro = State()
    NewLocationName = State()
    NewLocationAddress = State()
    SaveNewLocation = State()

    DeleteLocation = State()

    LocalObjectMetro = State()
    LocalObjectLocation = State()
    LocalObjectName = State()
    LocalObjectNameMore = State()

    RemoveLocalObject = State()

    NewCategory = State()
    OneMoreNewCategory = State()

    RemoveCategory = State()

    ItemCategory = State()
    ItemName = State()
    ItemPhoto = State()
    ItemDescription = State()
    ItemSize = State()
    ItemPrice = State()
    ItemConfirm = State()

    ItemSizeNameFirst = State()
    ItemSizePriceFirst = State()
    ItemSizeConfirmFirst = State()

    ItemSizeName = State()
    ItemSizePrice = State()
    ItemSizeConfirm = State()

    OneMoreProductSize = State()

    RemoveItemCategory = State()
    RemoveItem = State()

    AdminSellerName = State()
    AdminSellerID = State()
    AdminSellerMetro = State()
    AdminSellerLocation = State()

    RemoveSellerAdmin = State()
    ResetSellerAdmin = State()

    SellerName = State()
    SellerID = State()
    SellerMetro = State()
    SellerLocation = State()

    RemoveSeller = State()
    ResetSeller = State()

    CourierName = State()
    CourierID = State()
    CourierMetro = State()
    CourierLocation = State()

    RemoveCourier = State()
    ResetCourier = State()

    RemoveCategoryFromStocks = State()
    ReturnCategoryToStocks = State()

    ReturnItemToStockCategory = State()
    ReturnItemToStockProduct = State()

    RemoveItemFromStockCategory = State()
    RemoveItemFromStockProduct = State()

    ChangeSellerAdmin = State()
    ChangeSellerAdminMetro = State()
    ChangeSellerAdminLocation = State()

    ChangeSeller = State()
    ChangeSellerMetro = State()
    ChangeSellerLocation = State()

    ChangeCourier = State()
    ChangeCourierMetro = State()
    ChangeCourierLocation = State()

    EditMetro = State()
    EditMetroName = State()

    EditItem = State()
    EditItemById = State()
    EditItemByWaitSubject = State()
    EditItemByName = State()
    EditItemByDescription = State()
    EditItemByPhoto = State()
    EditItemByPrices = State()
    EditItemByAvailability = State()
    EditItemBySizes = State()

    EditItemNewSizeName = State()
    EditItemNewSizePrices = State()

    EditItemRemoveSizes = State()

    EditItemEditSizes = State()

    EditItemEditSizeById = State()
    EditItemEditSizeByIdName = State()
    EditItemEditSizeByIdPrices = State()

    DeliveryCategoryName = State()
    DeliveryItemCategory = State()
    DeliveryItemName = State()
    DeliveryItemPrice = State()

    TakeOrders = State()
    SetCourierOrders = State()
    ConfirmDeliveryOrders = State()
    TakeOrdersWait = State()

    RemoveDeliveryCategory = State()
    RemoveDeliveryItemCat = State()
    RemoveDeliveryItem = State()

    RemoveDeliveryItemFromStockCategory = State()
    RemoveDeliveryItemFromStockProduct = State()

    ReturnDeliveryItemToStockCategory = State()
    ReturnDeliveryItemToStockProduct = State()

    EditDeliveryItem = State()
    EditDeliveryItemPrice = State()
    EditDeliveryItemID = State()

    DeliveryCourierName = State()
    DeliveryCourierID = State()
    RemoveDeliveryCourier = State()


