from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.callback_datas import back_to_product_list_data, product_count_price_data, \
    back_to_product_from_sizes_list_data, back_to_size_from_price_list_data
from keyboards.inline.inline_keyboards import generate_keyboard_with_categories, generate_keyboard_with_products, \
    generate_keyboard_with_count_and_prices, one_more_product_markup, delivery_options_markup, \
    generate_keyboard_with_sizes, generate_keyboard_with_count_and_prices_for_size
from loader import dp, db, bot
from states.menu_states import Menu
from utils.temp_orders_list import get_temp_orders_list_message, get_final_price


@dp.callback_query_handler(text='back', state=Menu.WaitCategory)
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
    await call.message.answer('Выберите категорию меню',
                              reply_markup=await generate_keyboard_with_categories(call.from_user.id))
    await Menu.WaitCategory.set()


@dp.callback_query_handler(back_to_product_list_data.filter(), state=Menu.WaitQuantity)
async def back_to_product(call: CallbackQuery, callback_data: dict):
    """Назад к выбору товара без размеров"""
    await call.answer(cache_time=10)
    category_id = int(callback_data.get('category_id'))
    print(category_id)
    await call.message.edit_reply_markup()
    await call.message.answer('Выберите товар',
                              reply_markup=await generate_keyboard_with_products(call.from_user.id, category_id))

    await Menu.WaitProduct.set()


@dp.callback_query_handler(back_to_product_from_sizes_list_data.filter(), state=Menu.WaitProductSizeBack)
async def back_to_product_from_sizes_list(call: CallbackQuery, callback_data: dict):
    """Назад к выбору товара из меню выбора размера"""
    await call.answer(cache_time=10)
    category_id = int(callback_data.get('category_id'))
    print(category_id)
    await call.message.edit_reply_markup()
    await call.message.answer('Выберите товар',
                              reply_markup=await generate_keyboard_with_products(call.from_user.id, category_id))
    await db.delete_from_cart(call.from_user.id)

    await Menu.WaitProduct.set()


@dp.callback_query_handler(back_to_product_from_sizes_list_data.filter(), state=Menu.WaitProductSize)
async def back_to_product_from_sizes_list(call: CallbackQuery, callback_data: dict):
    """Назад к выбору товара из меню выбора размера"""
    await call.answer(cache_time=10)
    category_id = int(callback_data.get('category_id'))
    print(category_id)
    await call.message.edit_reply_markup()
    await call.message.answer('Выберите товар',
                              reply_markup=await generate_keyboard_with_products(call.from_user.id, category_id))

    await Menu.WaitProduct.set()


@dp.callback_query_handler(back_to_size_from_price_list_data.filter(), state=Menu.WaitQuantityBack)
async def back_to_size(call: CallbackQuery, callback_data: dict):
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
                                                                              product_info['product_info'][
                                                                                  'product_category_id']))
    await Menu.WaitProductSizeBack.set()


@dp.callback_query_handler(back_to_size_from_price_list_data.filter(), state=Menu.WaitQuantity)
async def back_to_size(call: CallbackQuery, callback_data: dict):
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
                                                                              product_info['product_info'][
                                                                                  'product_category_id']))
    await Menu.WaitProductSize.set()


@dp.callback_query_handler(back_to_product_list_data.filter(), state=Menu.WaitQuantityBack)
async def back_to_product(call: CallbackQuery, callback_data: dict):
    """Назад к выбору товара без размеров"""
    await call.answer(cache_time=10)
    category_id = int(callback_data.get('category_id'))
    print(category_id)
    await call.message.edit_reply_markup()
    await db.delete_from_cart(call.from_user.id)
    await call.message.answer('Выберите товар',
                              reply_markup=await generate_keyboard_with_products(call.from_user.id, category_id))

    await Menu.WaitProduct.set()


@dp.callback_query_handler(text='to_menu_one_more_product', state=Menu.OneMoreOrNext)
async def one_more_product(call: CallbackQuery):
    """Еще один товар"""
    await call.message.edit_reply_markup()
    await call.message.answer('Выберите категорию меню',
                              reply_markup=await generate_keyboard_with_categories(call.from_user.id))
    await Menu.WaitCategory.set()


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
        await Menu.WaitQuantityBack.set()


@dp.callback_query_handler(product_count_price_data.filter(quantity='6'), state=[Menu.WaitQuantityBack,
                                                                                 Menu.WaitQuantityFromSize])
async def set_quntity_more_than_6_back(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Пользователь ввел 6+"""
    await call.message.edit_reply_markup()
    price = int(callback_data.get('price'))
    await state.update_data(price=price)
    await call.message.answer("Пожалуйста, напишите количество товара (6 или больше)")
    if state.get_state() == 'Menu:WaitQuantityBack':
        await Menu.WaitQuantity6Back.set()
    else:
        await Menu.WaitQuantity6FromSize.set()


@dp.message_handler(regexp="\d+", state=[Menu.WaitQuantity6Back, Menu.WaitQuantity6FromSize])
async def get_quantity_more_than_6_back(message: types.Message, state: FSMContext):
    print(message.text)
    try:
        quantity = int(message.text)
        if quantity < 6:
            await message.answer("Пожалуйста, напишите количество товара (6 или больше)")
            await Menu.WaitQuantity6Back.set()
        else:
            data = await state.get_data()
            product_price = data.get('price')
            order_price = quantity * product_price
            order_id = data.get('order_id')
            if state.get_state() == 'Menu:WaitQuantity6FromSize':
                size_id= data.get('order_detail["size_id"]')
                await db.update_quantity_size_and_price(order_id, product_price, quantity, order_price, size_id)
            else:
                await db.update_quantity_and_price(order_id, product_price, quantity, order_price)
            await state.finish()
            await Menu.OneMoreOrNext.set()
            temp_orders = await db.get_temp_orders(message.from_user.id)
            list_products = await get_temp_orders_list_message(temp_orders)
            final_price = await get_final_price(temp_orders)
            await state.update_data(list_products=list_products)
            await state.update_data(final_price=final_price)
            await message.answer(text=f'Вы выбрали:\n{list_products}')
            await message.answer(f'Сумма заказа - {final_price} руб.',
                                 reply_markup=one_more_product_markup)
            await message.answer(text='Оформить заказ\n'
                                      'i Доставка работает в будни с 11 до 17',
                                 reply_markup=delivery_options_markup)

    except:
        await message.answer("Пожалуйста, напишите количество товара (6 или больше)")
        await Menu.WaitQuantity6Back.set()


@dp.callback_query_handler(product_count_price_data.filter(), state=[Menu.WaitQuantityBack,
                                                                     Menu.WaitQuantityFromSize])
async def set_quntity(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Пользователь ввел меньше 6"""
    await call.message.edit_reply_markup()
    product_price = int(callback_data.get('price'))
    quantity = int(callback_data.get('quantity'))
    order_price = product_price * quantity
    data = await state.get_data()
    order_id = data.get('order_id')
    if state.get_state() == 'Menu:WaitQuantity6FromSize':
        size_id = data.get('order_detail["size_id"]')
        await db.update_quantity_size_and_price(order_id, product_price, quantity, order_price, size_id)
    else:
        await db.update_quantity_and_price(order_id, product_price, quantity, order_price)

    await state.finish()
    await Menu.OneMoreOrNext.set()
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
