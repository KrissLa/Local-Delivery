import logging

from aiogram import types
from aiogram.types import CallbackQuery

from filters.users_filters import IsAdminMessage
from keyboards.inline.callback_datas import categories_data
from keyboards.inline.inline_keyboards import cancel_admin_markup
from loader import dp, db
from states.admin_state import AddAdmin
from utils.emoji import attention_em, error_em, success_em
from utils.temp_orders_list import get_list_of_delivery_products_for_return_to_stock, \
    get_list_of_delivery_products_for_remove_from_stock, get_list_of_products_for_return_to_stock, \
    get_list_of_products_for_remove_from_stock


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.RemoveItemFromStockCategory)
async def get_category_for_remove_item_from_stock(call: CallbackQuery, callback_data: dict):
    """Получаем категорию из которой будем убирать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_products_for_remove_from_stock(category_id)
    if products:
        list_of_products = await get_list_of_products_for_remove_from_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров в продаже',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.RemoveItemFromStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_item_from_stock_by_id_\d+",
                    state=AddAdmin.RemoveItemFromStockProduct)
async def remove_item_from_stock_by_id(message: types.Message):
    """Убираем товар с продажи"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_item(product_id)
        await message.answer(f'{success_em} Товар снят с продажи')
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.ReturnItemToStockCategory)
async def get_category_for_return_item_to_stock(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, в которую будем возвращать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_products_for_return_to_stock(category_id)
    if products:
        list_of_products = await get_list_of_products_for_return_to_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров, снятых с продажи',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.ReturnItemToStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="return_item_to_stock_by_id_\d+",
                    state=AddAdmin.ReturnItemToStockProduct)
async def return_item_to_stock_by_id(message: types.Message):
    """Возвращаем товар"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.return_to_stock_item(product_id)
        await message.answer(f'{success_em} Товар возвращен в продажу')
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="remove_from_stock_category_by_id_\d+",
                    state=AddAdmin.RemoveCategoryFromStocks)
async def remove_category_from_stock_by_id(message: types.Message):
    """Убираем категорию из меню"""
    try:
        category_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_category(category_id)
        await message.answer(f'{success_em} Категория снята с продажи')
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="return_to_stock_category_by_id_\d+",
                    state=AddAdmin.ReturnCategoryToStocks)
async def return_category_from_stock_by_id(message: types.Message):
    """Возврат категории в меню"""
    try:
        category_id = int(message.text.split('_')[-1])
        await db.return_to_stock_category(category_id)
        await message.answer(f'{success_em} Категория возвращена в продажу')
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.RemoveDeliveryItemFromStockCategory)
async def get_category_delivery(call: CallbackQuery, callback_data: dict):
    """Получаем категорию из которой будем убирать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_delivery_products_for_remove_from_stock(category_id)
    if products:
        list_of_products = await get_list_of_delivery_products_for_remove_from_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров в продаже',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.RemoveDeliveryItemFromStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_delivery_item_from_stock_by_id_\d+",
                    state=AddAdmin.RemoveDeliveryItemFromStockProduct)
async def remove_delivery_item_from_stock_by_id(message: types.Message):
    """Убираем товар с продажи"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_delivery_item(product_id)
        await message.answer(f'{success_em}Товар снят с продажи')
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.ReturnDeliveryItemToStockCategory)
async def get_category_delivery(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, и показываем список товаров, снятых с продажи"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_delivery_products_for_return_to_stock(category_id)
    if products:
        list_of_products = await get_list_of_delivery_products_for_return_to_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров, снятых с продажи',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.ReturnDeliveryItemToStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="return_delivery_item_to_stock_by_id_\d+",
                    state=AddAdmin.ReturnDeliveryItemToStockProduct)
async def return_delivery_item_to_stock_by_id(message: types.Message):
    """Возвращаем товар"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.return_to_stock_delivery_item(product_id)
        await message.answer(f'{success_em} Товар возвращен в продажу\n'
                             f'{attention_em} Чтобы вернуть еще один снова введите /return_delivery_item_to_stock\n'
                             f'{attention_em} Чтобы убрать из продажи введите /remove_delivery_item_from_stock')
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)
