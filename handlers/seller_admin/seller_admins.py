import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import IsSellerAdminMessage
from keyboards.inline.callback_datas import categories_data
from keyboards.inline.inline_keyboards import cancel_admin_markup
from loader import dp, db, bot
from states.seller_admin_states import SellerAdmin
from utils.emoji import attention_em_red, attention_em, error_em, success_em
from utils.statistics import send_confirm_mail
from utils.temp_orders_list import get_list_of_products_for_remove_from_stock, get_list_of_products_for_return_to_stock


# @dp.callback_query_handler(back_to_product_list_data.filter(), state=SellerAdmin.DeliveryQuantity)
# async def back_to_products_list(call: CallbackQuery, callback_data: dict, state: FSMContext):
#     """Назад к выбору товара"""
#     logging.info(callback_data)
#     category_id = int(callback_data.get('category_id'))
#     await call.message.edit_reply_markup()
#     data = await state.get_data()
#     delivery_order = data.get('delivery_order')
#     delivery_order['category_id'] = category_id
#     await state.update_data(delivery_order=delivery_order)
#     products = await db.get_delivery_products(category_id)
#     if products:
#         await call.message.answer(f'Создание заказа на поставку.\n'
#                                   f'Адрес доставки: {delivery_order["address"]}\n'
#                                   f'Выберите позицию.',
#                                   reply_markup=await generate_keyboard_with_delivery_products(products))
#     else:
#         await call.message.answer('Нет доступных товаров.',
#                                   reply_markup=await generate_keyboard_with_none_products())
#     await SellerAdmin.DeliveryProduct.set()


@dp.message_handler(state=SellerAdmin.SellerName)
async def get_seller_name(message: types.Message, state: FSMContext):
    """ПОлучаем имя продацва"""
    seller_name = message.text
    await state.update_data(seller_name=seller_name)
    await message.answer(f"Отлично!\n"
                         f"Имя продавца - {seller_name}\n"
                         f"Теперь введите telegramID продавца. \n"
                         f"{attention_em}Взять id сотрудник может в этом боте @myidbot\n"
                         f"{attention_em_red} Пользователю будет отправлено сообщение о назначении должности. "
                         f"Поэтому он должен отправить боту хотя бы одно сообщение перед назначением.",
                         reply_markup=cancel_admin_markup)
    await SellerAdmin.SellerTelegramID.set()


@dp.message_handler(state=SellerAdmin.SellerTelegramID)
async def get_seller_telegram_id(message: types.Message, state: FSMContext):
    """Получаем телеграм id"""
    try:
        seller_id = int(message.text)
        data = await state.get_data()
        seller_name = data.get('seller_name')
        location_id = data.get('location_id')
        metro_id = data.get('metro_id')

        await bot.send_message(seller_id, 'Вам назначили должность "Продавец"')
        if await db.add_seller(seller_id, seller_name, metro_id, location_id):
            await message.answer('Продавец успешно добавлен.')
            await state.finish()
        else:
            await message.answer(f'{error_em} Продавец с таким id уже добавлен')
            await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Не получается добавить пользователя. Возможно, он не отправил боту сообщение.'
                             'Попробуйте еще раз.',
                             reply_markup=cancel_admin_markup)
        await SellerAdmin.SellerTelegramID.set()


@dp.message_handler(regexp="remove_seller_\d+", state=SellerAdmin.RemoveSeller)
async def remove_seller_by_id(message: types.Message, state: FSMContext):
    """Удаляем продавца"""
    try:
        data = await state.get_data()
        location_id = data.get('location_id')
        seller_id = int(message.text.split('_')[-1])
        seller_location_id = await db.get_seller_location(seller_id)
        if location_id == seller_location_id:
            await db.delete_seller_by_id(seller_id)
            await message.answer('Продавец удален. \n'
                                 f'{attention_em} Чтобы удалить еще одного снова введите /remove_sellers_')
        else:
            await message.answer(f'{error_em} Вы не можете удалить продавца из другой локации')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(state=SellerAdmin.CourierName)
async def get_courier_name(message: types.Message, state: FSMContext):
    """ПОлучаем имя курьера"""
    courier_name = message.text
    await state.update_data(courier_name=courier_name)
    await message.answer(f"Отлично!\n"
                         f"Имя курьера - {courier_name}\n"
                         f"Теперь введите telegramID курьера. \n"
                         f"{attention_em} Взять id сотрудник может в этом боте @myidbot\n"
                         f"{attention_em_red} Пользователю будет отправлено сообщение о назначении должности. "
                         f"Поэтому он должен отправить боту хотя бы одно сообщение перед назначением.",
                         reply_markup=cancel_admin_markup)
    await SellerAdmin.CourierTelegramID.set()


@dp.message_handler(state=SellerAdmin.CourierTelegramID)
async def get_courier_telegram_id(message: types.Message, state: FSMContext):
    """Получаем телеграм id"""
    try:
        courier_id = int(message.text)
        data = await state.get_data()
        courier_name = data.get('courier_name')
        location_id = data.get('location_id')
        metro_id = data.get('metro_id')

        await bot.send_message(courier_id, 'Вам назначили должность "Курьер"')
        if await db.add_courier(courier_id, courier_name, metro_id, location_id):
            await message.answer('Курьер успешно добавлен.')
            await state.finish()
        else:
            await message.answer(f'{error_em} Курьер с таким id уже добавлен')
            await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Не получается добавить пользователя. Возможно, он не отправил боту сообщение.'
                             'Попробуйте еще раз.',
                             reply_markup=cancel_admin_markup)
        await SellerAdmin.CourierTelegramID.set()


@dp.message_handler(regexp="remove_courier_\d+", state=SellerAdmin.RemoveCourier)
async def remove_courier_by_id(message: types.Message, state: FSMContext):
    """Удаляем курьера"""
    try:
        courier_id = int(message.text.split('_')[-1])
        courier_location_id = await db.get_courier_location(courier_id)
        data = await state.get_data()
        location_id = data.get('location_id')
        if location_id == courier_location_id:
            await db.delete_courier_by_id(courier_id)
            await message.answer('Курьер удален. \n'
                                 f'{attention_em} Чтобы удалить еще одного снова введите /remove_courier_')
        else:
            await message.answer(f'{error_em} Вы не можете удалить курьера из другой локации')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(regexp="remove_from_stock_category_by_id_\d+", state=SellerAdmin.RemoveCategoryFromStock)
async def remove_category_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем категорию с продажи"""
    try:
        data = await state.get_data()
        location_id = data.get('location_id')
        category_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_category_in_location(category_id, location_id)
        await message.answer('Категория снята с продажи\n'
                             f'{attention_em} Чтобы снять еще одну снова введите /remove_category_from_stock\n'
                             f'{attention_em} Чтобы вернуть в продажу введите /return_category_to_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(regexp="return_to_stock_category_by_id_\d+", state=SellerAdmin.ReturnCategoryToStock)
async def remove_category_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем категорию с продажи"""
    try:
        data = await state.get_data()
        location_id = data.get('location_id')
        category_id = int(message.text.split('_')[-1])
        await db.return_from_stock_category_in_location(category_id, location_id)
        await message.answer('Категория возвращена в продажу\n'
                             f'{attention_em} Чтобы вернуть еще одну снова введите /return_category_to_stock\n'
                             f'{attention_em} Чтобы убрать из продажи введите /remove_category_from_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=SellerAdmin.RemoveItemFromStockCategory)
async def get_category_for_remove_item_from_stock(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем категорию из которой будем убирать товар"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    location_id = data.get('location_id')
    category_id = int(callback_data.get('category_id'))
    products = await db.get_products_for_stock_in_location(location_id, category_id, 'true')
    if products:
        list_of_products = await get_list_of_products_for_remove_from_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров в продаже',
                                  reply_markup=cancel_admin_markup)
    await SellerAdmin.RemoveItemFromStockProduct.set()


@dp.message_handler(regexp="remove_item_from_stock_by_id_\d+", state=SellerAdmin.RemoveItemFromStockProduct)
async def remove_item_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем товар с продажи"""
    try:
        data = await state.get_data()
        location_id = data.get('location_id')
        product_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_product_in_location(product_id, location_id)
        await message.answer('Товар снят с продажи\n'
                             f'{attention_em} Чтобы снять еще один снова введите /remove_item_from_stock\n'
                             f'{attention_em} Чтобы вернуть в продажу введите /return_item_to_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=SellerAdmin.ReturnItemToStockCategory)
async def get_category_for_return_item_to_stock(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем категорию, в которую будем возвращать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    data = await state.get_data()
    location_id = data.get('location_id')
    products = await db.get_products_for_stock_in_location(location_id, category_id, 'false')
    if products:
        list_of_products = await get_list_of_products_for_return_to_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров, снятых с продажи',
                                  reply_markup=cancel_admin_markup)
    await SellerAdmin.ReturnItemToStockProduct.set()


@dp.message_handler(regexp="return_item_to_stock_by_id_\d+", state=SellerAdmin.ReturnItemToStockProduct)
async def return_item_to_stock_by_id(message: types.Message, state: FSMContext):
    """Возвращаем товар"""
    try:
        product_id = int(message.text.split('_')[-1])
        data = await state.get_data()
        location_id = data.get('location_id')
        await db.return_to_stock_product_in_location(product_id, location_id)
        await message.answer('Товар возвращен в продажу\n'
                             f'{attention_em} Чтобы вернуть еще один снова введите /return_item_to_stock\n'
                             f'{attention_em} Чтобы убрать из продажи введите /remove_item_from_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(text='cancel', state=[SellerAdmin.SellerName,
                                                 SellerAdmin.SellerTelegramID,
                                                 SellerAdmin.RemoveSeller,
                                                 SellerAdmin.CourierName,
                                                 SellerAdmin.CourierTelegramID,
                                                 SellerAdmin.RemoveCourier,
                                                 SellerAdmin.RemoveCategoryFromStock,
                                                 SellerAdmin.ReturnCategoryToStock,
                                                 SellerAdmin.RemoveItemFromStockCategory,
                                                 SellerAdmin.RemoveItemFromStockProduct,
                                                 SellerAdmin.ReturnItemToStockCategory,
                                                 SellerAdmin.ReturnItemToStockProduct,
                                                 SellerAdmin.ChangeOrder,
                                                 SellerAdmin.ChangeDeliveryWaitConfirm])
async def cancel_add_admin(call: CallbackQuery, state: FSMContext):
    """Кнопка отмены"""
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Вы отменили операцию')


@dp.message_handler(IsSellerAdminMessage(), state=SellerAdmin.Email)
async def update_email(message: types.Message, state: FSMContext):
    """Обновляем email"""
    email = message.text
    name = await db.get_seller_admin_data(message.from_user.id)
    logging.info(email)
    try:
        send_confirm_mail('Уведомление о привязке почты',
                          f'Пользователь {name} привязал этот email-адрес для получения статистики.',
                          email)
        await db.update_email(email, message.from_user.id)
        await message.answer(f'{success_em} E-mail адрес {email} успешно привязан.')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Не получилось привязать E-mail адрес {email}.\n'
                             f'Проверьте правильность и введите адрес еще раз.')
