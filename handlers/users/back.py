from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.callback_datas import back_to_product_list_data, back_to_product_from_sizes_list_data, \
    back_to_size_from_price_list_data
from keyboards.inline.inline_keyboards import generate_keyboard_with_categories, generate_keyboard_with_products, \
    generate_keyboard_with_sizes, generate_keyboard_with_count_and_prices, \
    generate_keyboard_with_count_and_prices_for_size, one_more_product_markup, delivery_options_markup, \
    need_pass_markup, build_keyboard_with_time, generate_keyboard_with_none_categories, \
    generate_keyboard_with_none_products
from loader import dp, db, bot
from states.menu_states import Menu
from utils.temp_orders_list import get_temp_orders_list_message, get_final_price, get_couriers_list


@dp.callback_query_handler(text='back_main', state=Menu.WaitCategory)
async def back_from_menu(call: CallbackQuery, state: FSMContext):
    """Выход из меню"""
    await call.message.edit_reply_markup()
    await call.answer("Вы вышли из меню")
    await state.finish()


@dp.callback_query_handler(text='back', state=Menu.WaitProduct)
async def back_to_category(call: CallbackQuery):
    """Назад к выбору категории"""
    await call.message.edit_reply_markup()
    await call.answer("Вы нажали назад")
    categories = await db.get_categories_for_user_location_id(call.from_user.id)
    if categories:
        await call.message.answer('Выберите категорию меню',
                                  reply_markup=await generate_keyboard_with_categories(categories))
    else:
        await call.message.answer('Нет доступных категорий.',
                                  reply_markup=await generate_keyboard_with_none_categories())
    await Menu.WaitCategory.set()


@dp.callback_query_handler(back_to_product_list_data.filter(), state=[Menu.WaitQuantity, Menu.WaitQuantityBack])
async def back_to_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Назад к выбору товара без размеров"""
    await call.message.edit_reply_markup()
    await call.answer(cache_time=10)
    if await state.get_state() == 'Menu:WaitQuantityBack':
        await db.delete_from_cart(call.from_user.id)
    category_id = int(callback_data.get('category_id'))
    products = await db.get_product_for_user_location_id(call.from_user.id, category_id)
    if products:
        await call.message.answer('Выберите товар',
                                  reply_markup=await generate_keyboard_with_products(products))
    else:
        await call.message.answer('Нет доступных товаров.',
                                  reply_markup=await generate_keyboard_with_none_products())

    await Menu.WaitProduct.set()


@dp.callback_query_handler(back_to_product_list_data.filter(), state=[Menu.WaitProductSize,
                                                                      Menu.WaitProductSizeBack])
async def back_to_product_from_sizes_list(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Назад к выбору товара из меню выбора размера"""
    print('Поймал')
    if await state.get_state() == 'Menu:WaitProductSizeBack':
        await db.delete_from_cart(call.from_user.id)
    await call.answer(cache_time=10)
    category_id = int(callback_data.get('category_id'))
    products = await db.get_product_for_user_location_id(call.from_user.id, category_id)
    await call.message.edit_reply_markup()
    if products:
        await call.message.answer('Выберите товар',
                                  reply_markup=await generate_keyboard_with_products(products))
    else:
        await call.message.answer('Нет доступных товаров.',
                                  reply_markup=await generate_keyboard_with_none_products())

    await Menu.WaitProduct.set()


@dp.callback_query_handler(back_to_size_from_price_list_data.filter(), state=[Menu.WaitQuantity,
                                                                              Menu.WaitQuantityBackWithSize])
async def back_to_size(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Назад к выбору размера товара"""
    await call.message.edit_reply_markup()
    product_id = int(callback_data.get('product_id'))
    product_info = await db.get_product_info_by_id(product_id, call.from_user.id)
    print(product_info['product_info']['product_category_id'])
    await bot.send_photo(chat_id=call.from_user.id,
                         photo=product_info['product_info']['product_photo_id'],
                         caption=product_info['product_info']['product_description'])
    await call.message.answer('Для заказа выберите размер.',
                              reply_markup=await generate_keyboard_with_sizes(product_info['list_of_sizes'],
                                                                              product_info['product_info']
                                                                              ['product_category_id']))
    if await state.get_state() == 'Menu:WaitQuantity':
        await Menu.WaitProductSize.set()
    else:
        await Menu.WaitProductSizeBack.set()


@dp.callback_query_handler(text='back', state=Menu.OneMoreOrNext)
async def back_to_quantity(call: CallbackQuery, state: FSMContext):
    """Назад к выбору количества"""
    await call.message.edit_reply_markup()
    product_data = await db.get_last_temp_order_id(call.from_user.id)
    print(product_data)
    product_id = product_data['product_id']
    order_id = product_data['temp_order_id']
    size_id = product_data['size_id']
    await state.update_data(order_id=order_id)
    product_info = await db.get_product_info_by_id(product_id, call.from_user.id)
    if not size_id:
        await bot.send_photo(chat_id=call.from_user.id,
                             photo=product_info['product_photo_id'],
                             caption=product_info['product_description'])
        await call.message.answer("Укажите количество:",
                                  reply_markup=await generate_keyboard_with_count_and_prices(product_info))
        await Menu.WaitQuantityBack.set()
    else:
        await bot.send_photo(chat_id=call.from_user.id,
                             photo=product_info['product_info']['product_photo_id'],
                             caption=product_info['product_info']['product_description'])
        size_info = await db.get_size_info(size_id)
        await call.message.answer("Укажите количество:",
                                  reply_markup=await generate_keyboard_with_count_and_prices_for_size(size_info,
                                                                                                      product_id))
        await Menu.WaitQuantityBackWithSize.set()


@dp.callback_query_handler(text='back', state=[Menu.WaitTime, Menu.WaitAddress])
async def back_to_one_more_or_next(call: CallbackQuery, state: FSMContext):
    """Возврат к меню выбора способа доставки"""
    await call.message.edit_reply_markup()
    temp_orders = await db.get_temp_orders(call.from_user.id)
    list_products = await get_temp_orders_list_message(temp_orders)
    final_price = await get_final_price(temp_orders)
    await state.update_data(list_products=list_products)
    await state.update_data(final_price=final_price)
    await call.message.answer(text=f'Вы выбрали:\n{list_products}')
    await call.message.answer(f'Сумма заказа - {final_price} руб.',
                              reply_markup=one_more_product_markup)
    await call.message.answer(text='Оформить заказ\n'
                                   'i Доставка работает в будни с 11 до 17',
                              reply_markup=delivery_options_markup)
    await Menu.OneMoreOrNext.set()


@dp.callback_query_handler(text='back_to_pass', state=Menu.WaitTime)
async def back_to_pass(call: CallbackQuery):
    """Назад к выбору нужен ли пропуск"""
    await call.message.edit_reply_markup()
    order_data = await db.get_last_user_order_detail(user_id=call.from_user.id)
    couriers_list = await db.get_couriers_list(order_data['order_location_id'])
    await call.message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                              f'{order_data["order_info"]}\n'
                              f'Адрес доставки: {order_data["order_local_object_name"]},\n'
                              f'{order_data["delivery_address"]}\n'
                              f'Сумма заказа - {order_data["order_price"]} руб.')
    await call.message.answer(f'Внимание! Закажите гостевой пропуск для курьеров в случае необходимости.\n'
                              f'ФИО курьеров:\n{await get_couriers_list(couriers_list)}\n'
                              f'Один из них доставит Вам заказ',
                              reply_markup=need_pass_markup)
    await Menu.WaitPass.set()


@dp.callback_query_handler(text='back', state=[Menu.WaitUserConfirmationDelivery, Menu.WaitUserConfirmationPickup])
async def back_to_time(call: CallbackQuery, state: FSMContext):
    """Возвращаемся к клавиатуре с временем"""
    await call.message.edit_reply_markup()
    order_data = await db.get_last_user_order_detail(user_id=call.from_user.id)
    if await state.get_state() == "Menu:WaitUserConfirmationDelivery":
        order_pass_value = await db.get_order_pass_value(order_data['order_id'])
        await call.message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                                  f'{order_data["order_info"]}\n'
                                  f'Адрес доставки: {order_data["order_local_object_name"]}, \n'
                                  f'{order_data["delivery_address"]}\n'
                                  f'{order_pass_value}\n'
                                  f'Сумма заказа - {order_data["order_price"]} руб.')
        await call.message.answer('Выберите время через которое необходимо доставить Ваш заказ:',
                                  reply_markup=await build_keyboard_with_time('delivery', 'back_to_pass'))
    else:
        await call.message.answer(f'Ваш заказ № {order_data["order_id"]}:\n'
                                  f'{order_data["order_info"]}\n'
                                  f'Адрес самовывоза: {order_data["delivery_address"]}\n'
                                  f'Сумма заказа - {order_data["order_price"]} руб.\n'
                                  f'Выберите время, через которое необходимо приготовить Ваш заказ:',
                                  reply_markup=await build_keyboard_with_time('pickup', 'back'))
    await Menu.WaitTime.set()
