import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import IsAdminMessage
from keyboards.inline.callback_datas import categories_data
from keyboards.inline.inline_keyboards import cancel_admin_markup
from loader import dp, db
from states.admin_state import AddAdmin
from utils.emoji import attention_em, error_em, success_em
from utils.temp_orders_list import get_list_of_delivery_products_for_edit


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.EditDeliveryItem)
async def get_category(call: CallbackQuery, callback_data: dict):
    """Получаем категорию и выдаем список с товарами"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_delivery_products_list(category_id)
    if products:
        list_of_products = await get_list_of_delivery_products_for_edit(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.EditDeliveryItemID.set()


@dp.message_handler(IsAdminMessage(), regexp="edit_delivery_item_price_by_id_\d+",
                    state=AddAdmin.EditDeliveryItemID)
async def get_item(message: types.Message, state: FSMContext):
    """Просим ввести новую цену"""
    try:
        product_id = int(message.text.split('_')[-1])
        await state.update_data(item_id=product_id)
        item = await db.get_delivery_product_by_id(product_id)
        await state.update_data(item_name=item["delivery_product_name"])
        logging.info(item)
        await message.answer(f'ID товара - {item["delivery_product_id"]}\n'
                             f'Название - {item["delivery_product_name"]}\n'
                             f'Цена за лоток - {item["delivery_price"]} руб.\n\n'
                             f'{attention_em} Чтобы изменить цену введите ее.\n'
                             f'Пример:\n'
                             f'2100',
                             reply_markup=cancel_admin_markup)
        await AddAdmin.EditDeliveryItemPrice.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), state=AddAdmin.EditDeliveryItemPrice)
async def get_new_price(message: types.Message, state: FSMContext):
    """Получаем новую цену"""
    try:
        price = int(message.text)
        data = await state.get_data()
        item_id = data.get('item_id')
        item_name = data.get('item_name')
        await db.update_delivery_product_price(item_id, price)
        await message.answer(f'{success_em} Цена обновлена!\n'
                             f'ID товара - {item_id}\n'
                             f'Название товара: {item_name}\n'
                             f'Новая цена за 1 лоток (12шт): {price} руб.')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f"{error_em} Вам нужно ввести число.\n"
                             f'Пример: \n'
                             f'1650',
                             reply_markup=cancel_admin_markup)
