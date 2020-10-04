import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import categories_data, product_list_data, size_product_data, \
    product_count_price_data, need_pass_data, deliver_to_time_data
from keyboards.inline.inline_keyboards import generate_keyboard_with_categories, generate_keyboard_with_products, \
    generate_keyboard_with_count_and_prices, generate_keyboard_with_sizes, \
    generate_keyboard_with_count_and_prices_for_size, delivery_options_markup, \
    order_cancel_or_back_markup, need_pass_markup, \
    build_keyboard_with_time, confirm_order_markup, generate_keyboard_with_none_categories, \
    generate_keyboard_with_none_products, back_button
from loader import dp, db, bot
from states.menu_states import Menu
from utils.emoji import attention_em, warning_em
from utils.send_messages import send_message_to_sellers, send_cart
from utils.temp_orders_list import get_temp_orders_list_message, get_final_price, get_couriers_list


@dp.callback_query_handler(text='to_menu_one_more_product', state=Menu.OneMoreOrNext)
async def one_more_product(call: CallbackQuery, state: FSMContext):
    """Добавить еще один товар"""
    await state.finish()
    await call.message.edit_reply_markup()
    categories = await db.get_categories_for_user_location_id(call.from_user.id)
    if categories:
        await call.message.answer('Выберите категорию меню',
                                  reply_markup=await generate_keyboard_with_categories(categories))
    else:
        await call.message.answer('Нет доступных категорий.',
                                  reply_markup=await generate_keyboard_with_none_categories())
    await Menu.WaitCategory.set()


@dp.callback_query_handler(categories_data.filter(), state=Menu.WaitCategory)
async def send_products(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отправляем товары из выбранной категории, доступные в локации пользователя"""
    await call.message.edit_reply_markup()
    await call.answer(cache_time=10)
    category_id = callback_data.get('category_id')
    await state.update_data(category_id=category_id)
    products = await db.get_product_for_user_location_id(call.from_user.id, category_id)
    if products:
        await call.message.edit_reply_markup(await generate_keyboard_with_products(products))
    else:
        await call.message.answer('Нет доступных товаров.',
                                  reply_markup=await generate_keyboard_with_none_products())
    await Menu.WaitProduct.set()


@dp.callback_query_handler(product_list_data.filter(), state=Menu.WaitProduct)
async def send_product_info(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отправляем описание и цену товара.
        Если у товара есть разные размеры отправляем их.
        Если нет, сразу предлагаем выбрать количество"""
    await call.message.edit_reply_markup()
    product_id = int(callback_data.get('product_id'))
    product_info = await db.get_product_info_by_id(product_id, call.from_user.id)
    if len(product_info) == 10:
        order_detail = {
            'product_id': int(product_id),
            'product_name': product_info['product_name'],
            'size_id': None
        }
        await bot.send_photo(chat_id=call.from_user.id,
                             photo=product_info['product_photo_id'],
                             caption=product_info['product_description'])
        await call.message.answer("Укажите количество:",
                                  reply_markup=await generate_keyboard_with_count_and_prices(product_info))
        await state.update_data(order_detail=order_detail)
        await Menu.WaitQuantity.set()
    elif len(product_info) == 2:
        await bot.send_photo(chat_id=call.from_user.id,
                             photo=product_info['product_info']['product_photo_id'],
                             caption=product_info['product_info']['product_description'])
        await call.message.answer('Для заказа выберите размер.',
                                  reply_markup=await generate_keyboard_with_sizes(product_info['list_of_sizes'],
                                                                                  product_info['product_info'][
                                                                                      'product_category_id']))
        await Menu.WaitProductSize.set()


@dp.callback_query_handler(size_product_data.filter(), state=[Menu.WaitProductSize, Menu.WaitProductSizeBack])
async def get_product_size(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем размер товара"""
    product_id = int(callback_data.get('product_id'))
    size_id = int(callback_data.get('size_id'))
    size_info = await db.get_size_info(size_id)
    product_name = await db.get_product_name(product_id)
    prod_size_name = f'{product_name}, {size_info["size_name"]}'
    order_detail = {
        'product_id': int(product_id),
        'product_name': prod_size_name,
        'size_id': int(size_id)
    }
    await state.update_data(order_detail=order_detail)
    await call.message.answer("Укажите количество:",
                              reply_markup=await generate_keyboard_with_count_and_prices_for_size(size_info,
                                                                                                  product_id))
    if await state.get_state() == 'Menu:WaitProductSize':
        await Menu.WaitQuantity.set()
    else:
        await Menu.WaitQuantityBackWithSizeId.set()


@dp.callback_query_handler(product_count_price_data.filter(quantity='6'), state=[Menu.WaitQuantity,
                                                                                 Menu.WaitQuantityBack,
                                                                                 Menu.WaitQuantityBackWithSize,
                                                                                 Menu.WaitQuantityBackWithSizeId])
async def set_quntity_more_than_6(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Пользователь ввел 6+"""
    await call.message.edit_reply_markup()
    price = callback_data.get('price')
    order_data = await state.get_data()
    order_data['order_detail']['product_price'] = int(price)
    await state.update_data(order_detail=order_data['order_detail'])
    await call.message.answer("Пожалуйста, напишите количество товара (6 или больше)")
    if await state.get_state() == 'Menu:WaitQuantity':
        await Menu.WaitQuantity6.set()
    elif await state.get_state() == 'Menu:WaitQuantityBack':
        await Menu.WaitQuantity6Back.set()
    elif await state.get_state() == 'Menu:WaitQuantityBackWithSize':
        await Menu.WaitQuantity6BackWithSize.set()
    else:
        await Menu.WaitQuantity6BackWithSizeId.set()


@dp.message_handler(regexp="\d+", state=[Menu.WaitQuantity6,
                                         Menu.WaitQuantity6Back,
                                         Menu.WaitQuantity6BackWithSize,
                                         Menu.WaitQuantity6BackWithSizeId])
async def get_quantity_more_than_6(message: types.Message, state: FSMContext):
    """Ловим количество больше 6"""
    try:
        quantity = int(message.text)
        if quantity < 6:
            await message.answer(f"{warning_em} Пожалуйста, напишите количество товара (6 или больше)")
            if await state.get_state() == 'Menu:WaitQuantity6BackWithSize':
                await Menu.WaitQuantity6BackWithSize.set()
            elif await state.get_state() == 'Menu:WaitQuantity6Back':
                await Menu.WaitQuantity6Back.set()
            elif await state.get_state() == 'Menu:WaitQuantity6BackWithSizeId':
                await Menu.WaitQuantity6BackWithSizeId.set()
            else:
                await Menu.WaitQuantity6.set()
        else:

            order_data = await state.get_data()
            product_price = order_data['order_detail']['product_price']
            order_price = product_price * quantity
            order_data['order_detail']['quantity'] = quantity
            order_data['order_detail']['order_price'] = order_price
            size_id = order_data["order_detail"]["size_id"]
            if await state.get_state() in ['Menu:WaitQuantity6BackWithSize', 'Menu:WaitQuantity6Back']:
                order_id = int(order_data.get('order_id'))
                await db.update_quantity_and_price(order_id, product_price, quantity, order_price)
            elif await state.get_state() == 'Menu:WaitQuantity6BackWithSizeId':
                order_id = int(order_data.get('order_id'))
                await db.update_quantity_size_and_price(order_id, product_price, quantity, order_price, size_id,
                                                        order_data['order_detail']['product_name'])
            else:
                await db.add_temp_order(message.from_user.id, order_data['order_detail'])
            temp_orders = await db.get_temp_orders(message.from_user.id)
            await Menu.OneMoreOrNext.set()

            await send_cart(temp_orders, message.from_user.id)
            final_price = await get_final_price(temp_orders)
            list_products = await get_temp_orders_list_message(temp_orders)
            await state.update_data(list_products=list_products)
            await state.update_data(final_price=final_price)
            await message.answer(text=f'Сумма заказа - {final_price} руб.\n'
                                      'Оформить заказ\n'
                                      f'{attention_em} Доставка работает в будни с 11 до 17',
                                 reply_markup=delivery_options_markup)
    except Exception as err:
        logging.error(err)
        await message.answer(f"{warning_em} Пожалуйста, напишите количество товара (6 или больше)")
        if await state.get_state() == 'Menu:WaitQuantity6BackWithSize':
            await Menu.WaitQuantity6BackWithSize.set()
        elif await state.get_state() == 'Menu:WaitQuantity6Back':
            await Menu.WaitQuantity6Back.set()
        elif await state.get_state() == 'Menu:WaitQuantity6BackWithSizeId':
            await Menu.WaitQuantity6BackWithSizeId.set()
        else:
            await Menu.WaitQuantity6.set()


@dp.callback_query_handler(product_count_price_data.filter(), state=[Menu.WaitQuantity,
                                                                     Menu.WaitQuantityBack,
                                                                     Menu.WaitQuantityBackWithSize,
                                                                     Menu.WaitQuantityBackWithSizeId])
async def set_quantity(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Пользователь ввел меньше 6"""
    await call.message.edit_reply_markup()
    price = int(callback_data.get('price'))
    quantity = int(callback_data.get('quantity'))
    order_price = price * quantity
    order_data = await state.get_data()
    order_data['order_detail']['product_price'] = int(price)
    order_data['order_detail']['quantity'] = quantity
    order_data['order_detail']['order_price'] = order_price
    if await state.get_state() in ['Menu:WaitQuantityBackWithSize', 'Menu:WaitQuantityBack']:
        order_id = await db.get_last_temp_order_only_id(call.from_user.id)
        await db.update_quantity_and_price(order_id, order_data['order_detail']['product_price'], quantity, order_price)
    elif await state.get_state() == 'Menu:WaitQuantityBackWithSizeId':
        order_id = await db.get_last_temp_order_only_id(call.from_user.id)
        await db.update_quantity_size_and_price(order_id, order_data['order_detail']['product_price'], quantity,
                                                order_price, order_data['order_detail']['size_id'],
                                                order_data['order_detail']['product_name'])
    else:
        await db.add_temp_order(call.from_user.id, order_data['order_detail'])
    await Menu.OneMoreOrNext.set()
    temp_orders = await db.get_temp_orders(call.from_user.id)
    list_products = await get_temp_orders_list_message(temp_orders)
    final_price = await get_final_price(temp_orders)
    await state.update_data(list_products=list_products)
    await state.update_data(final_price=final_price)
    await send_cart(temp_orders, call.from_user.id)
    await call.message.answer(text=f'Сумма заказа - {final_price} руб.\n'
                                   'Оформить заказ\n'
                                   f'{attention_em} Доставка работает в будни с 11 до 17',
                              reply_markup=delivery_options_markup)


@dp.callback_query_handler(text='delivery_option_pickup', state=Menu.OneMoreOrNext)
async def set_pickup(call: CallbackQuery, state: FSMContext):
    """Пользователь выбирает самовывоз"""
    st_data = await state.get_data()
    list_products = st_data.get('list_products')
    if list_products:
        await call.message.edit_reply_markup()
        user_id = call.from_user.id
        user_data = await db.get_user_address_data(user_id)

        order_price = st_data.get('final_price')

        await db.add_order_pickup(order_user_telegram_id=user_id,
                                  order_metro_id=user_data['user_metro_id'],
                                  order_location_id=user_data['user_location_id'],
                                  order_local_object_id=user_data['user_local_object_id'],
                                  order_local_object_name=user_data['local_object_name'],
                                  delivery_method='Заберу сам',
                                  delivery_address=user_data['location_address'],
                                  order_info=list_products,
                                  order_price=order_price,
                                  order_status='Ожидание пользователя')
        order_id = await db.get_last_order_id(user_id)
        await call.message.answer(f'Ваш заказ № {order_id}:\n'
                                  f'{list_products}\n'
                                  f'Адрес самовывоза: {user_data["location_address"]}\n'
                                  f'Сумма заказа - {order_price} руб.\n'
                                  f'Выберите время, через которое необходимо приготовить Ваш заказ:',
                                  reply_markup=await build_keyboard_with_time('pickup', 'back'))
        await Menu.WaitTime.set()
    else:
        await call.message.edit_reply_markup()
        await call.message.answer(f'{warning_em} Для заказа Вам нужно выбрать хотя бы один товар.  Выберите что-то'
                                  f' из меню.')


@dp.callback_query_handler(text='back', state=[Menu.WaitPass,
                                               Menu.WaitNewAddress])
@dp.callback_query_handler(text='delivery_option_delivery', state=Menu.OneMoreOrNext)
async def set_delivery(call: CallbackQuery, state: FSMContext):
    """Пользователь выбирает с доставкой"""
    st_data = await state.get_data()
    list_products = st_data.get('list_products')
    if list_products:
        order_price = st_data.get('final_price')
        await call.message.edit_reply_markup()
        if await state.get_state() == 'Menu:WaitPass':
            await call.answer("Вернулись к адресу")
            await call.message.answer("Вернулись к адресу")
        user_id = call.from_user.id
        user_data = await db.get_user_address_data_without_location_address(user_id)
        await state.update_data(user_local_object_name=user_data['local_object_name'])

        await db.add_order(order_user_telegram_id=user_id,
                           order_metro_id=user_data['user_metro_id'],
                           order_location_id=user_data['user_location_id'],
                           order_local_object_id=user_data['user_local_object_id'],
                           order_local_object_name=user_data['local_object_name'],
                           delivery_method='С доставкой',
                           order_info=list_products,
                           order_price=order_price,
                           order_status='Ожидание пользователя')
        order_id = await db.get_last_order_id(user_id)
        await call.message.answer(f'Ваш заказ № {order_id}:\n'
                                  f'{list_products}\n'
                                  f'Адрес доставки: {user_data["local_object_name"]}\n'
                                  f'Сумма заказа - {order_price} руб.')
        if user_data['user_address'] is None:
            await call.message.answer('Напишите точное место доставки и телефон для связи.\n\n'
                                      'Пример 1: Подъезд 2, 15 этаж, офис 123, ООО Компания, ФИО покупателя, 89160000000\n\n'
                                      'Пример 2: Северный вход, у ресепшн, 89160000000.',
                                      reply_markup=order_cancel_or_back_markup)
        else:
            await state.update_data(address=user_data['user_address'])
            await call.message.answer(f"Использовать адрес предыдущего заказа?\n{user_data['user_address']}",
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                          [
                                              InlineKeyboardButton(
                                                  text='Да, использовать адрес',
                                                  callback_data='use_previous_address'
                                              )
                                          ],
                                          [
                                              InlineKeyboardButton(
                                                  text='Ввести новый адрес',
                                                  callback_data='input_new_address'
                                              )
                                          ],
                                          [
                                              back_button
                                          ]
                                      ]))
        await Menu.WaitAddress.set()
    else:
        await call.message.edit_reply_markup()
        await call.message.answer(f'{warning_em} Для заказа Вам нужно выбрать хотя бы один товар. Выберите что-то из'
                                  f' меню.')


@dp.callback_query_handler(text='use_previous_address', state=Menu.WaitAddress)
async def use_previous_address(call: CallbackQuery, state: FSMContext):
    """Используем предыдущий адрес"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    address = data.get('address')

    order_data = await db.get_last_user_order_detail(user_id=call.from_user.id)
    await db.update_order_address(order_id=order_data["order_id"], address=address)
    couriers_list = await db.get_couriers_list(order_data['order_location_id'])
    await call.message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                              f'{order_data["order_info"]}\n'
                              f'Адрес доставки: {order_data["order_local_object_name"]}, {address}\n'
                              f'Сумма заказа - {order_data["order_price"]} руб.')
    if couriers_list:
        await call.message.answer(f'Внимание! Закажите гостевой пропуск для курьеров в случае необходимости.\n'
                                  f'ФИО курьеров:\n{await get_couriers_list(couriers_list)}\n'
                                  f'Один из них доставит Вам заказ',
                                  reply_markup=need_pass_markup)
    else:
        await call.message.answer(f'Внимание! Закажите гостевой пропуск для курьера в случае необходимости.\n'
                                  f'ФИО курьера: Отправим после подтверждения заказа\n',
                                  reply_markup=need_pass_markup)
    await Menu.WaitPass.set()


@dp.callback_query_handler(text='input_new_address', state=Menu.WaitAddress)
async def use_previous_address(call: CallbackQuery, state: FSMContext):
    """Просим ввести новый адрес"""
    await call.message.edit_reply_markup()
    await call.message.answer('Напишите точное место доставки и телефон для связи.\n\n'
                              'Пример 1: Подъезд 2, 15 этаж, офис 123, ООО Компания, ФИО покупателя, 89160000000\n\n'
                              'Пример 2: Северный вход, у ресепшн, 89160000000.',
                              reply_markup=order_cancel_or_back_markup)
    await Menu.WaitNewAddress.set()


@dp.message_handler(state=Menu.WaitNewAddress)
async def get_user_address(message: types.Message):
    """Получаем адес доставки от пользователя"""
    address = message.text
    order_data = await db.get_last_user_order_detail(user_id=message.from_user.id)
    await db.update_order_address(order_id=order_data["order_id"], address=address)
    await db.update_user_address(message.from_user.id, address)
    couriers_list = await db.get_couriers_list(order_data['order_location_id'])
    await message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                         f'{order_data["order_info"]}\n'
                         f'Адрес доставки: {order_data["order_local_object_name"]}, {address}\n'
                         f'Сумма заказа - {order_data["order_price"]} руб.')
    if couriers_list:
        await message.answer(f'Внимание! Закажите гостевой пропуск для курьеров в случае необходимости.\n'
                             f'ФИО курьеров:\n{await get_couriers_list(couriers_list)}\n'
                             f'Один из них доставит Вам заказ',
                             reply_markup=need_pass_markup)
    else:
        await message.answer(f'Внимание! Закажите гостевой пропуск для курьера в случае необходимости.\n'
                             f'ФИО курьера: Отправим после подтверждения заказа\n',
                             reply_markup=need_pass_markup)
    await Menu.WaitPass.set()


@dp.callback_query_handler(need_pass_data.filter(), state=Menu.WaitPass)
async def is_pass_need(call: CallbackQuery, callback_data: dict):
    """Выбираем нужен ли пропуск"""
    status = callback_data.get('status')
    await call.message.edit_reply_markup()
    order_data = await db.get_last_user_order_detail(user_id=call.from_user.id)
    couriers_list = await db.get_couriers_list(order_data['order_location_id'])
    if status == 'True':
        if couriers_list:
            order_pass_value = f'Пропуск заказан для: \n{await get_couriers_list(couriers_list)}\n'
        else:
            order_pass_value = f'Пропуск будет заказан позже\n'
    else:
        order_pass_value = f'Пропуск не требуется'
    await db.update_order_pass(order_data['order_id'], order_pass_value)

    await call.message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                              f'{order_data["order_info"]}\n'
                              f'Адрес доставки: {order_data["order_local_object_name"]}, \n'
                              f'{order_data["delivery_address"]}\n'
                              f'{order_pass_value}\n'
                              f'Сумма заказа - {order_data["order_price"]} руб.')
    await call.message.answer('Выберите время, через которое необходимо доставить Ваш заказ:',
                              reply_markup=await build_keyboard_with_time('delivery', 'back_to_pass'))
    await Menu.WaitTime.set()


@dp.callback_query_handler(deliver_to_time_data.filter(), state=Menu.WaitTime)
async def get_time_of_delivery(call: CallbackQuery, callback_data: dict):
    """Получаем время через которое нужно доставить заказ"""
    await call.message.edit_reply_markup()
    min = int(callback_data.get('time'))
    time = callback_data.get('value')
    order_data = await db.get_last_user_order_detail(user_id=call.from_user.id)
    await db.update_time_for_delivery(order_id=order_data['order_id'], time_value=min)
    if order_data['delivery_method'] == 'С доставкой':
        await call.message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                                  f'{order_data["order_info"]}\n'
                                  f'Адрес доставки: {order_data["order_local_object_name"]},\n'
                                  f'{order_data["delivery_address"]}\n'
                                  f'{order_data["order_pass_for_courier"]}\n'
                                  f'Доставить через {time}\n'
                                  f'Сумма заказа - {order_data["order_price"]} руб.',
                                  reply_markup=confirm_order_markup)
        await Menu.WaitUserConfirmationDelivery.set()
    else:
        await call.message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                                  f'{order_data["order_info"]}\n'
                                  f'Адрес самовывоза: {order_data["delivery_address"]}\n'
                                  f'Приготовоить через {time}\n'
                                  f'Сумма заказа - {order_data["order_price"]} руб.',
                                  reply_markup=confirm_order_markup)
        await Menu.WaitUserConfirmationPickup.set()


@dp.callback_query_handler(text='confirm_order', state=[Menu.WaitUserConfirmationDelivery,
                                                        Menu.WaitUserConfirmationPickup])
async def user_confirm_order(call: CallbackQuery, state: FSMContext):
    """Пользователь подтвердил заказ"""
    await call.message.edit_reply_markup()
    order_id = await db.get_last_order_id(call.from_user.id)
    order_data = await db.get_last_user_order_detail_after_confirm(user_id=call.from_user.id)
    sellers_list = await db.get_sellers_id_for_location(order_data['order_location_id'])
    if sellers_list:
        await db.update_order_status_and_created_at(order_id, 'Ожидание подтверждения продавца')
        await send_message_to_sellers(sellers_list, order_data)
        await db.clear_cart(call.from_user.id)
        await call.message.answer(f"Готово.\n"
                                  f"Статус: {order_data['order_status']}\n")
        await state.finish()
    else:
        await call.message.answer(f"Извините. Не нашел доступных продавцов.\n"
                                  f"{attention_em} Ваши товары помещены в корзину: /cart\n"
                                  f"Если Вы считаете что произошла ошибка, пожалуйста свяжитесь с нами.")

        await state.finish()
