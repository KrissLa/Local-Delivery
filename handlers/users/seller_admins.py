import logging
from datetime import datetime, time, date

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone

from keyboards.inline.callback_datas import categories_data, delivery_categories_data, delivery_product_data, \
    back_to_product_list_data, delivery_product_count_data, remove_from_cart_data, delivery_date_data, \
    delivery_time_data
from keyboards.inline.inline_keyboards import cancel_admin_markup, generate_keyboard_with_none_categories, \
    generate_keyboard_with_delivery_categories, \
    generate_keyboard_with_none_products, generate_keyboard_with_delivery_products, \
    generate_keyboard_with_counts_for_delivery_products, add_delivery_order_markup, get_markup_with_date, time_markup, \
    confirm_delivery_order_markup, change_delivery_order_markup, change_and_cancel_delivery_order_markup, \
    get_markup_with_date_change, generate_time_markup, confirm_changes_markup, confirm_cancel_delivery
from loader import dp, db, bot
from states.seller_admin_states import SellerAdmin
from utils.emoji import attention_em_red, attention_em, warning_em, error_em, success_em
from utils.send_messages import send_delivery_cart
from utils.temp_orders_list import get_list_of_products_for_remove_from_stock, get_list_of_products_for_return_to_stock, \
    get_final_delivery_price, \
    get_temp_delivery_orders_list_message, get_list_of_delivery_orders, get_delivery_order_info_message, weekdays


@dp.message_handler(state=SellerAdmin.ChangeOrder, regexp="change_delivery_order_by_id_\d+")
async def get_delivery_order_info(message: types.Message, state: FSMContext):
    """Изменяем размер по id"""
    delivery_order_id = int(message.text.split('_')[-1])
    logging.info(delivery_order_id)
    if await db.is_user_owner(message.from_user.id, delivery_order_id):
        await state.update_data(delivery_order_id=delivery_order_id)
        now = datetime.now(timezone("Europe/Moscow"))
        now = now.replace(tzinfo=None)
        order_data = await db.get_delivery_order_data(delivery_order_id)
        delta_hours = (order_data['delivery_datetime'] - now).total_seconds() // 3600
        logging.info(delta_hours)
        order_info = await get_delivery_order_info_message(order_data)
        logging.info(delta_hours)
        logging.info(order_info)
        if delta_hours < 3:
            await message.answer(text=order_info + f'{warning_em} До доставки осталось меньше 3 часов!\n'
                                                   f' Вы больше не можете изменить или отменить заказ')
            await state.finish()
        elif delta_hours < 12:
            await message.answer(text=order_info +
                                      f'{warning_em} До доставки осталось меньше 12 часов. Вы больше не можете отменить '
                                      f'заказ, но можете изменить дату и время заказа на более поздние.\n'
                                      f'{attention_em_red} Внимание! После изменения даты/времени доставки, заказ отменить '
                                      f'будет нельзя',
                                 reply_markup=change_delivery_order_markup)
            await SellerAdmin.ChangeDeliveryDate.set()
        elif order_data['delivery_order_status'] in ['Заказ изменен', 'Заказ подтвержден после изменения']:
            await message.answer(text=order_info +
                                      f'{warning_em} Дата доставки уже менялась. Вы больше не можете отменить '
                                      f'заказ, но можете изменить дату и время заказа на более поздние.\n'
                                      f'{attention_em_red} Внимание! После изменения даты/времени доставки, заказ отменить '
                                      f'будет нельзя',
                                 reply_markup=change_delivery_order_markup)
            await SellerAdmin.ChangeDeliveryDate.set()
        else:
            await message.answer(text=order_info +
                                      f'{attention_em} Вы можете изменить дату и время доставки на более поздние или '
                                      f'отменить заказ.\n'
                                      f'{warning_em} Внимание! После изменения даты/времени доставки, заказ отменить '
                                      f'будет нельзя',
                                 reply_markup=change_and_cancel_delivery_order_markup)
            await SellerAdmin.ChangeDeliveryDate.set()
    else:
        await message.answer('У Вас нет доступа к этому заказу,\n'
                             'Вы в главном меню')
        await state.finish()


@dp.callback_query_handler(text='back', state=SellerAdmin.ChangeDeliveryDate)
async def back(call: CallbackQuery, state: FSMContext):
    """Назад к списку"""
    delivery_orders = await db.get_delivery_orders(call.from_user.id)
    if delivery_orders:
        await call.message.answer(await get_list_of_delivery_orders(delivery_orders),
                                  reply_markup=cancel_admin_markup)

    else:
        await call.message.answer('Нет активных заказов',
                                  reply_markup=cancel_admin_markup)
    await SellerAdmin.ChangeOrder.set()


@dp.callback_query_handler(text='back', state=[SellerAdmin.ChangeDeliveryTime,
                                               SellerAdmin.WaitCancelConfirm])
async def back(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order_id = data.get('delivery_order_id')
    logging.info(delivery_order_id)
    await state.update_data(delivery_order_id=delivery_order_id)
    now = datetime.now(timezone("Europe/Moscow"))
    now = now.replace(tzinfo=None)
    order_data = await db.get_delivery_order_data(delivery_order_id)
    delta_hours = (order_data['delivery_datetime'] - now).total_seconds() // 3600
    logging.info(delta_hours)
    order_info = await get_delivery_order_info_message(order_data)
    logging.info(delta_hours)
    logging.info(order_info)
    if delta_hours < 3:
        await call.message.answer(text=order_info + f'{warning_em} До доставки осталось меньше 3 часов!\n'
                                                    f' Вы больше не можете изменить или отменить заказ')
        await state.finish()
    elif delta_hours < 12:
        await call.message.answer(text=order_info +
                                       f'{warning_em} До доставки осталось меньше 12 часов. Вы больше не можете отменить '
                                       f'заказ, но можете изменить дату и время заказа на более поздние.\n'
                                       f'{attention_em_red} Внимание! После изменения даты/времени доставки, заказ отменить '
                                       f'будет нельзя',
                                  reply_markup=change_delivery_order_markup)
        await SellerAdmin.ChangeDeliveryDate.set()
    elif order_data['delivery_order_status'] in ['Заказ изменен', 'Заказ подтвержден после изменения']:
        await call.message.answer(text=order_info +
                                       f'{warning_em} Дата доставки уже менялась. Вы больше не можете отменить '
                                       f'заказ, но можете изменить дату и время заказа на более поздние.\n'
                                       f'{attention_em_red} Внимание! После изменения даты/времени доставки, заказ отменить '
                                       f'будет нельзя',
                                  reply_markup=change_delivery_order_markup)
        await SellerAdmin.ChangeDeliveryDate.set()
    else:
        await call.message.answer(text=order_info +
                                       f'{attention_em} Вы можете изменить дату и время доставки на более поздние или '
                                       f'отменить заказ.\n'
                                       f'{warning_em} Внимание! После изменения даты/времени доставки, заказ отменить '
                                       f'будет нельзя',
                                  reply_markup=change_and_cancel_delivery_order_markup)
        await SellerAdmin.ChangeDeliveryDate.set()


@dp.callback_query_handler(text='cancel_delivery_order', state=SellerAdmin.ChangeDeliveryDate)
async def cancel_delivery_order(call: CallbackQuery):
    """Отмена заказа"""
    await call.message.edit_reply_markup()
    await call.message.answer('Подтвердите отмену заказа.',
                              reply_markup=confirm_cancel_delivery)
    await SellerAdmin.WaitCancelConfirm.set()


@dp.callback_query_handler(text='confirm_cancel_delivery', state=SellerAdmin.WaitCancelConfirm)
async def cancel_delivery_order_confirm(call: CallbackQuery, state: FSMContext):
    """Отмена заказа"""
    data = await state.get_data()
    delivery_order_id = data.get('delivery_order_id')
    await db.cancel_delivery_order(delivery_order_id)
    order_data = await db.get_delivery_order_data(delivery_order_id)
    admins = await db.get_admins_list()
    for admin in admins:
        try:
            await bot.send_message(admin["admin_telegram_id"], f'{error_em} Заказ № {delivery_order_id} отменен.\n'
                                                               f'Адрес доставки: {order_data["location_name"]},\n'
                                                               f'{order_data["location_address"]}.\n'
                                                               f'{order_data["delivery_order_info"]}'
                                                               f'Стоимость заказа: '
                                                               f'{order_data["delivery_order_price"]} руб.\n'
                                                               f'Дата доставки: '
                                                               f'{order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                                                               f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                                                               f'Время доставки: '
                                                               f'{order_data["delivery_time_info"]}\n'
                                                               f'Статус заказа: '
                                                               f'{order_data["delivery_order_status"]}\n')
        except Exception as err:
            logging.info(admin["admin_telegram_id"])
            logging.error(err)
    await call.message.answer(f'{success_em} Заказ № {delivery_order_id} успешно отменен.\n')
    await state.finish()


@dp.callback_query_handler(text='back', state=SellerAdmin.ChangeDeliveryConfirm)
@dp.callback_query_handler(text='change_delivery_time', state=SellerAdmin.ChangeDeliveryDate)
async def change_delivery_date(call: CallbackQuery, state: FSMContext):
    """Выдаем клавиатуру с датами"""
    data = await state.get_data()
    delivery_order_id = data.get('delivery_order_id')
    order_data = await db.get_delivery_order_data(delivery_order_id)
    await call.message.answer(f'Изменение времени доставки заказа № {order_data["delivery_order_id"]}.\n'
                              f'Адрес доставки: {order_data["location_name"]},\n'
                              f'{order_data["location_address"]}.\n'
                              f'{order_data["delivery_order_info"]}'
                              f'Стоимость заказа: {order_data["delivery_order_price"]} руб.\n'
                              f'Дата доставки: {order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                              f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                              f'Время доставки: {order_data["delivery_time_info"]}\n'
                              f'Статус заказа: {order_data["delivery_order_status"]}\n\n'
                              f'Укажите новую дату доставки.',
                              reply_markup=await get_markup_with_date_change(order_data['delivery_datetime']))
    await SellerAdmin.ChangeDeliveryTime.set()


@dp.callback_query_handler(text='back', state=SellerAdmin.ChangeDeliveryWaitConfirm)
@dp.callback_query_handler(delivery_date_data.filter(), state=SellerAdmin.ChangeDeliveryTime)
async def get_date(call: CallbackQuery, state: FSMContext, callback_data: dict = None):
    """Получаем дату заказа"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order_id = data.get('delivery_order_id')
    order_data = await db.get_delivery_order_data(delivery_order_id)
    if await state.get_state() == 'SellerAdmin:ChangeDeliveryWaitConfirm':
        changed_info = data.get('changed_info')
        new_order_date = changed_info['new_order_date']
        weekday = changed_info["weekday"]
    else:
        new_order_date = callback_data.get('date')
        weekday = callback_data.get('weekday')
    date_list = new_order_date.split('.')
    delivery_date = date(int(date_list[2]), int(date_list[1]), int(date_list[0]))

    if delivery_date == order_data['day_for_delivery']:
        markup = await generate_time_markup(order_data['delivery_time_info'])
    else:
        markup = time_markup
    await state.update_data(changed_info={'new_order_date': new_order_date,
                                          'weekday': weekday})
    await call.message.answer(f'Изменение времени доставки заказа № {delivery_order_id}.\n'
                              f'Адрес доставки: {order_data["location_name"]},\n'
                              f'{order_data["location_address"]}.\n'
                              f'{order_data["delivery_order_info"]}'
                              f'Стоимость заказа: {order_data["delivery_order_price"]} руб.\n'
                              f'Дата доставки: {order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                              f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                              f'Время доставки: {order_data["delivery_time_info"]}\n'
                              f'Статус заказа: {order_data["delivery_order_status"]}\n'
                              f'{attention_em} Новая дата доставки: {new_order_date} {weekday}\n\n'
                              f'Укажите новое время доставки.\n'
                              f'Текущее время (МСК): {datetime.now(timezone("Europe/Moscow")).strftime("%H:%M  %d.%m.%Y")}',
                              reply_markup=markup)
    await SellerAdmin.ChangeDeliveryConfirm.set()


@dp.callback_query_handler(delivery_time_data.filter(), state=SellerAdmin.ChangeDeliveryConfirm)
async def get_time(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем время доставки"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order_id = data.get('delivery_order_id')
    order_data = await db.get_delivery_order_data(delivery_order_id)
    changed_info = data.get('changed_info')
    changed_info['choice'] = callback_data.get('choice')
    changed_info['delivery_time'] = int(callback_data.get('time'))

    await state.update_data(changed_info=changed_info)
    await call.message.answer(f'Изменение времени доставки заказа № {delivery_order_id}.\n'
                              f'Адрес доставки: {order_data["location_name"]},\n'
                              f'{order_data["location_address"]}.\n'
                              f'{order_data["delivery_order_info"]}'
                              f'Стоимость заказа: {order_data["delivery_order_price"]} руб.\n'
                              f'Дата доставки: {order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                              f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                              f'Время доставки: {order_data["delivery_time_info"]}\n'
                              f'Статус заказа: {order_data["delivery_order_status"]}\n'
                              f'{attention_em} Новая дата доставки: {changed_info["new_order_date"]} '
                              f'{changed_info["weekday"]}\n\n'
                              f'{attention_em} Новое время доставки: {changed_info["choice"]}\n\n'
                              f'Сохраняем изменения?.\n',
                              reply_markup=confirm_changes_markup)
    await SellerAdmin.ChangeDeliveryWaitConfirm.set()


@dp.callback_query_handler(text='confirm_changes', state=SellerAdmin.ChangeDeliveryWaitConfirm)
async def save_changes(call: CallbackQuery, state: FSMContext):
    """Вносим изменения в заказ"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order_id = data.get('delivery_order_id')
    changed_info = data.get('changed_info')
    logging.info(changed_info)
    date_info = changed_info['new_order_date'].split('.')
    changed_info['new_delivery_date'] = date(int(date_info[2]), int(date_info[1]), int(date_info[0]))
    changed_info['new_delivery_time'] = time(changed_info['delivery_time'], 0)
    changed_info['new_delivery_datetime'] = datetime.combine(changed_info['new_delivery_date'],
                                                             changed_info['new_delivery_time'])
    logging.info(changed_info)
    await db.update_delivery_order(delivery_order_id, changed_info)
    order_data = await db.get_delivery_order_data(delivery_order_id)
    admins = await db.get_admins_list()
    for admin in admins:
        try:
            await bot.send_message(admin["admin_telegram_id"], f'{attention_em_red} Изменена дата доставки заказа'
                                                               f' № {delivery_order_id}.\n'
                                                               f'Адрес доставки: {order_data["location_name"]},\n'
                                                               f'{order_data["location_address"]}.\n'
                                                               f'{order_data["delivery_order_info"]}'
                                                               f'Стоимость заказа: '
                                                               f'{order_data["delivery_order_price"]} руб.\n'
                                                               f'Новая дата доставки: '
                                                               f'{order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                                                               f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                                                               f'Новое время доставки: '
                                                               f'{order_data["delivery_time_info"]}\n'
                                                               f'Статус заказа: '
                                                               f'{order_data["delivery_order_status"]}\n'
                                                               f'{attention_em} Чтобы принять или отклонить нажмите '
                                                               f'/take_order_{delivery_order_id}\n'
                                                               f'{attention_em} Чтобы посмотреть список непринятых или'
                                                               f' измененных заказов нажмите /take_orders')
        except Exception as err:
            logging.info(admin["admin_telegram_id"])
            logging.error(err)
    await call.message.answer(f'{success_em} Дата доставки заказа  № {delivery_order_id} успешно изменена\n'
                              f'Адрес доставки: {order_data["location_name"]},\n'
                              f'{order_data["location_address"]}.\n'
                              f'{order_data["delivery_order_info"]}'
                              f'Стоимость заказа: '
                              f'{order_data["delivery_order_price"]} руб.\n'
                              f'Новая дата доставки: '
                              f'{order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                              f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                              f'Новое время доставки: '
                              f'{order_data["delivery_time_info"]}\n'
                              f'Статус заказа: '
                              f'{order_data["delivery_order_status"]}\n')
    await state.finish()


@dp.callback_query_handler(text='back_main', state=SellerAdmin.DeliveryCategory)
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    """Выход из оптового заказа"""
    await state.finish()
    await call.message.edit_reply_markup()
    await call.message.answer('Вы отменили заказ')


@dp.callback_query_handler(back_to_product_list_data.filter(), state=SellerAdmin.DeliveryQuantity)
@dp.callback_query_handler(delivery_categories_data.filter(), state=SellerAdmin.DeliveryCategory)
async def get_delivery_category(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем категорию товара"""
    category_id = int(callback_data.get('category_id'))
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    delivery_order['category_id'] = category_id
    await state.update_data(delivery_order=delivery_order)
    products = await db.get_delivery_products(category_id)
    if products:
        await call.message.answer(f'Создание заказа на поставку.\n'
                                  f'Адрес доставки: {delivery_order["address"]}\n'
                                  f'Выберите позицию.',
                                  reply_markup=await generate_keyboard_with_delivery_products(products))
    else:
        await call.message.answer('Нет доступных товаров.',
                                  reply_markup=await generate_keyboard_with_none_products())
    await SellerAdmin.DeliveryProduct.set()


@dp.callback_query_handler(text='back', state=SellerAdmin.DeliveryProduct)
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    """Выход из оптового заказа"""
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    await call.message.edit_reply_markup()
    categories = await db.get_delivery_categories()
    if categories:
        markup = await generate_keyboard_with_delivery_categories(categories)
    else:
        markup = await generate_keyboard_with_none_categories()

    await call.message.answer(f'Создание заказа на поставку.\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              f'Выберите категорию.',
                              reply_markup=markup)
    await SellerAdmin.DeliveryCategory.set()


@dp.callback_query_handler(delivery_product_data.filter(), state=[SellerAdmin.DeliveryProduct,
                                                                  SellerAdmin.DeliveryQuantity6,
                                                                  SellerAdmin.ConfirmTempOrder,
                                                                  SellerAdmin.ConfirmTempOrderRemoved])
async def get_delivery_products(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем информацию о товаре"""
    if await state.get_state() == 'SellerAdmin:ConfirmTempOrder':
        await db.delete_last_temp_delivery_order_by_user(call.from_user.id)
    await call.message.edit_reply_markup()
    product_id = int(callback_data.get('product_id'))
    product_name = await db.get_delivery_product_name_by_id(product_id)
    price = int(callback_data.get('price'))
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    delivery_order['product_id'] = product_id
    delivery_order['price'] = price
    delivery_order['product_name'] = product_name
    await state.update_data(delivery_order=delivery_order)
    await call.message.answer(f'Создание заказа на поставку.\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              f'Вы выбрали: {delivery_order["product_name"]}\n'
                              f'Выберите количество',
                              reply_markup=await generate_keyboard_with_counts_for_delivery_products(
                                  delivery_order["price"],
                                  delivery_order["category_id"]))
    await SellerAdmin.DeliveryQuantity.set()


@dp.callback_query_handler(delivery_product_count_data.filter(quantity='6+'), state=SellerAdmin.DeliveryQuantity)
async def more_than_6(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Ввод больше шести"""
    await call.message.edit_reply_markup()
    logging.info(callback_data)
    data = await state.get_data()
    price = int(callback_data.get('price'))
    delivery_order = data.get('delivery_order')
    delivery_order['price'] = price
    await state.update_data(delivery_order=delivery_order)
    await call.message.answer('Напишите количество лотков (6 или больше)',
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='Назад',
                                          callback_data=delivery_product_data.new(
                                              product_id=delivery_order['product_id'],
                                              price=delivery_order['price'])
                                      )
                                  ]
                              ]))
    await SellerAdmin.DeliveryQuantity6.set()


@dp.callback_query_handler(delivery_product_count_data.filter(), state=SellerAdmin.DeliveryQuantity)
async def get_cunt(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Ввод меньше 6"""
    await call.message.edit_reply_markup()
    price = int(callback_data.get('price'))
    quantity = int(callback_data.get('quantity'))
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    order_price = delivery_order['price'] * quantity
    delivery_order['price'] = price
    delivery_order['quantity'] = quantity
    delivery_order['order_price'] = order_price
    await db.add_temp_delivery_order(call.from_user.id, delivery_order)
    temp_orders = await db.get_temp_delivery_orders(call.from_user.id)
    await SellerAdmin.ConfirmTempOrder.set()
    await call.message.answer('Создание заказа на поставку.\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              'Вы выбрали:')
    await send_delivery_cart(temp_orders, call.from_user.id)
    final_price = await get_final_delivery_price(temp_orders)
    # list_products = await get_temp_delivery_orders_list_message(temp_orders)
    # await state.update_data(list_products=list_products)
    await state.update_data(final_price=final_price)
    await call.message.answer(text=f'Сумма заказа - {final_price} руб.\n',
                              reply_markup=await add_delivery_order_markup(delivery_order['product_id'],
                                                                           delivery_order['price']))


@dp.message_handler(regexp="\d+", state=[SellerAdmin.DeliveryQuantity6])
async def get_quantity_more_than_6(message: types.Message, state: FSMContext):
    """Ловим количество больше 6"""
    try:
        quantity = int(message.text)
        if quantity < 6:
            await message.answer(f"{warning_em} Пожалуйста, напишите количество лотков (6 или больше)")
            await SellerAdmin.DeliveryQuantity6.set()
        else:
            data = await state.get_data()
            delivery_order = data.get('delivery_order')
            order_price = delivery_order['price'] * quantity
            delivery_order['quantity'] = quantity
            delivery_order['order_price'] = order_price
            await db.add_temp_delivery_order(message.from_user.id, delivery_order)
            temp_orders = await db.get_temp_delivery_orders(message.from_user.id)
            await SellerAdmin.ConfirmTempOrder.set()
            await message.answer('Создание заказа на поставку.\n'
                                 f'Адрес доставки: {delivery_order["address"]}\n'
                                 'Вы выбрали:')
            await send_delivery_cart(temp_orders, message.from_user.id)
            final_price = await get_final_delivery_price(temp_orders)
            # list_products = await get_temp_delivery_orders_list_message(temp_orders)
            # await state.update_data(list_products=list_products)
            await state.update_data(final_price=final_price)
            await message.answer(text=f'Сумма заказа - {final_price} руб.\n',
                                 reply_markup=await add_delivery_order_markup(delivery_order['product_id'],
                                                                              delivery_order['price']))
    except Exception as err:
        logging.error(err)
        await message.answer(f"{warning_em} Пожалуйста, напишите количество лотков (6 или больше)")
        await SellerAdmin.DeliveryQuantity6.set()


@dp.callback_query_handler(remove_from_cart_data.filter(), state=[SellerAdmin.ConfirmTempOrder,
                                                                  SellerAdmin.ConfirmTempOrderRemoved])
async def remove_item_from_cart(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Убираем товары из корзины"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    if await db.is_last_delivery_order(call.from_user.id,
                                       order_id) or await state.get_state() == 'SellerAdmin:ConfirmTempOrderRemoved':
        await SellerAdmin.ConfirmTempOrderRemoved.set()
    await db.delete_temp_delivery_order_by_id(order_id)
    await call.answer('Готово')


@dp.callback_query_handler(text='add_delivery_order', state=[SellerAdmin.ConfirmTempOrder,
                                                             SellerAdmin.ConfirmTempOrderRemoved])
async def add_new_seller(call: CallbackQuery, state: FSMContext):
    """Новый оптовый заказ для производства"""
    await call.message.edit_reply_markup()
    await state.finish()
    location_id = await db.get_seller_admin_location(call.from_user.id)
    address_info = await db.get_delivery_address_for_seller_admin(call.from_user.id)
    delivery_order = {
        'address': f'{address_info["metro_name"]}, \n{address_info["location_name"]}, {address_info["location_address"]}',
        'location_id': location_id
    }
    await state.update_data(delivery_order=delivery_order)
    categories = await db.get_delivery_categories()
    if categories:
        markup = await generate_keyboard_with_delivery_categories(categories, wbb=False)
    else:
        markup = await generate_keyboard_with_none_categories()

    await call.message.answer(f'Создание заказа на поставку.\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              f'Выберите категорию.',
                              reply_markup=markup)
    await SellerAdmin.DeliveryCategory.set()


@dp.callback_query_handler(text='back', state=SellerAdmin.DeliveryTime)
@dp.callback_query_handler(text='registration_delivery_order', state=[SellerAdmin.ConfirmTempOrder,
                                                                      SellerAdmin.ConfirmTempOrderRemoved])
async def registration_delivery_order(call: CallbackQuery, state: FSMContext):
    """Регистрация заказа"""
    await call.message.edit_reply_markup()
    temp_orders = await db.get_temp_delivery_orders(call.from_user.id)
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    if temp_orders:
        list_products = await get_temp_delivery_orders_list_message(temp_orders)
        final_price = await get_final_delivery_price(temp_orders)
        delivery_order['final_price'] = final_price
        delivery_order['list_of_products'] = list_products
        await state.update_data(delivery_order=delivery_order)
        await call.message.answer(f'Создание заказа на поставку.\n'
                                  f'Адрес доставки: {delivery_order["address"]}\n'
                                  f'Вы выбрали:\n'
                                  f'{list_products}\n'
                                  f'Сумма заказа {final_price}\n\n'
                                  f'Укажите дату доставки.\n'
                                  f'{attention_em} Заказ на следующий день возможен до 17 часов.\n'
                                  f'Текущее время (МСК): {datetime.now(timezone("Europe/Moscow")).strftime("%H:%M  %d.%m.%Y")}',
                                  reply_markup=await get_markup_with_date())
        await SellerAdmin.DeliveryDate.set()
    else:
        categories = await db.get_delivery_categories()
        await call.message.answer(f'{warning_em} Вам нужно выбрать хотя бы один товар')
        if categories:
            markup = await generate_keyboard_with_delivery_categories(categories)
        else:
            markup = await generate_keyboard_with_none_categories()

        await call.message.answer(f'Создание заказа на поставку.\n'
                                  f'Адрес доставки: {delivery_order["address"]}\n'
                                  f'Выберите категорию.',
                                  reply_markup=markup)
        await SellerAdmin.DeliveryCategory.set()


@dp.callback_query_handler(text='back', state=SellerAdmin.DeliveryDate)
async def back(call: CallbackQuery, state: FSMContext):
    """Назад к оформлению заказа"""
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    temp_orders = await db.get_temp_delivery_orders(call.from_user.id)
    await SellerAdmin.ConfirmTempOrder.set()
    await call.message.answer('Создание заказа на поставку.\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              'Вы выбрали:')
    await send_delivery_cart(temp_orders, call.from_user.id)
    final_price = await get_final_delivery_price(temp_orders)
    await call.message.answer(text=f'Сумма заказа - {final_price} руб.\n',
                              reply_markup=await add_delivery_order_markup(delivery_order['product_id'],
                                                                           delivery_order['price']))


@dp.callback_query_handler(delivery_date_data.filter(), state=SellerAdmin.DeliveryDate)
async def get_date(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем дату заказа"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    date = callback_data.get('date')
    weekday = callback_data.get('weekday')
    delivery_order['date'] = date
    delivery_order['weekday'] = weekday
    await state.update_data(delivery_order=delivery_order)
    await call.message.answer(f'Создание заказа на поставку.\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              f'Вы выбрали:\n'
                              f'{delivery_order["list_of_products"]}\n'
                              f'Сумма заказа {delivery_order["final_price"]}\n\n'
                              f'Дата доставки: {delivery_order["date"]} {delivery_order["weekday"]}\n\n'
                              f'Укажите время доставки.\n'
                              f'Текущее время (МСК): {datetime.now(timezone("Europe/Moscow")).strftime("%H:%M  %d.%m.%Y")}',
                              reply_markup=time_markup)
    await SellerAdmin.DeliveryTime.set()


@dp.callback_query_handler(delivery_time_data.filter(), state=SellerAdmin.DeliveryTime)
async def get_time(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем время доставки"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    delivery_order['choice'] = callback_data.get('choice')

    delivery_order['delivery_time'] = int(callback_data.get('time'))

    await state.update_data(delivery_order=delivery_order)
    await call.message.answer('Готово\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              f'Вы выбрали:\n'
                              f'{delivery_order["list_of_products"]}\n'
                              f'Сумма заказа - {delivery_order["final_price"]} руб.\n'
                              f'Дата доставки: {delivery_order["date"]} {delivery_order["weekday"]}\n'
                              f'Время доставки: {delivery_order["choice"]}',
                              reply_markup=confirm_delivery_order_markup)
    await SellerAdmin.ConfirmOrder.set()


@dp.callback_query_handler(text='back', state=SellerAdmin.ConfirmOrder)
async def back_to_time(call: CallbackQuery, state: FSMContext):
    """Назад к выбору времени"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    delivery_order = data.get('delivery_order')
    await call.message.answer(f'Создание заказа на поставку.\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              f'Вы выбрали:\n'
                              f'{delivery_order["list_of_products"]}\n'
                              f'Сумма заказа {delivery_order["final_price"]}\n\n'
                              f'Дата доставки: {delivery_order["date"]} {delivery_order["weekday"]}\n\n'
                              f'Укажите время доставки.\n'
                              f'Текущее время (МСК): {datetime.now(timezone("Europe/Moscow")).strftime("%H:%M  %d.%m.%Y")}',
                              reply_markup=time_markup)
    await SellerAdmin.DeliveryTime.set()


@dp.callback_query_handler(text='cancel_delivery_order', state=SellerAdmin.ConfirmOrder)
async def cancel_delivery_order(call: CallbackQuery, state: FSMContext):
    """Отмена заказа"""
    await call.message.edit_reply_markup()
    await db.delete_temp_delivery_order_by_user_id(call.from_user.id)
    await state.finish()
    await call.message.answer('Вы отменили заказ!')


@dp.callback_query_handler(text='confirm_delivery_order', state=SellerAdmin.ConfirmOrder)
async def confirm_delivery_order(call: CallbackQuery, state: FSMContext):
    """Подтверждаем заказ"""
    data = await state.get_data()
    delivery_order = data.get('delivery_order')

    date_list = delivery_order['date'].split('.')
    delivery_date = date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
    delivery_order['delivery_date'] = date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
    logging.info(delivery_date)
    logging.info(delivery_order['delivery_date'])
    delivery_time = time(delivery_order['delivery_time'], 0)
    delivery_order['delivery_time'] = time(delivery_order['delivery_time'], 0)
    delivery_datetime = datetime.combine(delivery_date, delivery_time)
    delivery_order['delivery_datetime'] = datetime.combine(delivery_date, delivery_time)
    logging.info(delivery_time)
    logging.info(delivery_order['delivery_time'])
    logging.info(delivery_order['delivery_datetime'])
    logging.info(delivery_datetime)
    logging.info(delivery_order)
    await db.add_delivery_order(call.from_user.id, delivery_order)
    order_id = await db.get_delivery_order_id(call.from_user.id)
    admins = await db.get_admins_list()
    for admin in admins:
        try:
            await bot.send_message(admin["admin_telegram_id"], f'Новый заказ на поставку № {order_id}.\n'
                                                               f'Адрес доставки: {delivery_order["address"]}\n'
                                                               f'{delivery_order["list_of_products"]}\n'
                                                               f'Сумма заказа: {delivery_order["final_price"]} руб.\n'
                                                               f'Дата доставки: {delivery_order["date"]} '
                                                               f'{delivery_order["weekday"]}\n'
                                                               f'Время доставки: {delivery_order["choice"]}\n\n'
                                                               f'{attention_em} Чтобы принять или отклонить нажмите '
                                                               f'/take_order_{order_id}\n'
                                                               f'{attention_em} Чтобы посмотреть список непринятых или'
                                                               f' измененных заказов нажмите /take_orders'
                                   )
        except Exception as err:
            logging.info(admin["admin_telegram_id"])
            logging.error(err)

    await call.message.answer('Спасибо.\n'
                              f'Ваш заказ сформирован и отправлен на производство.\n'
                              f'Номер заказа: №{order_id}\n'
                              f'Адрес доставки: {delivery_order["address"]}\n'
                              f'{delivery_order["list_of_products"]}\n'
                              f'Сумма заказа: {delivery_order["final_price"]} руб.\n'
                              f'Дата доставки: {delivery_order["date"]} {delivery_order["weekday"]}\n'
                              f'Время доставки: {delivery_order["choice"]}\n\n'
                              f'{attention_em} Вы можете изменить время доставки на более позднее, но не позднее, '
                              f'чем за 3 часа до доставки\n'
                              f'{warning_em} Отменить заказ можно не позднее, чем за 12 часов до доставки\n'
                              f'/change_delivery_order')
    await db.delete_temp_delivery_order_by_user_id(call.from_user.id)
    await state.finish()


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
