import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import categories_data, product_list_data, size_data
from keyboards.inline.inline_keyboards import generate_keyboard_with_products, generate_keyboard_with_categories, \
    generate_keyboard_with_product_sizes, confirm_edit_item_price_markup
from loader import dp, db, bot
from states.seller_admin_states import SellerAdmin
from utils.emoji import error_em, attention_em, success_em
from utils.get_prices import get_price_list


@dp.callback_query_handler(text='back_main', state=SellerAdmin.EditItemPriceCommand)
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    """Нажатие на кнопку 'Назад' на клавиатуре выбора категории"""
    await state.finish()
    await call.message.edit_reply_markup()
    await call.message.answer('Вы отменили операцию')


@dp.callback_query_handler(categories_data.filter(), state=[SellerAdmin.EditItemPriceCommand,
                                                            SellerAdmin.EditItemPriceProduct,
                                                            SellerAdmin.EditItemPriceProductPrice])
async def choose_category(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Админ локации выбирает категорию.
    Выводим список товаров для изменеия цены."""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    await state.update_data(category_id=category_id)
    products = await db.get_products_list(category_id)
    await call.message.answer('Теперь выберите товар',
                              reply_markup=await generate_keyboard_with_products(products))
    await SellerAdmin.EditItemPriceCategory.set()


@dp.callback_query_handler(text='back', state=SellerAdmin.EditItemPriceCategory)
async def back(call: CallbackQuery, state: FSMContext):
    """Нажатие на кнопку 'Назад' на клавиатуре выбора товаров"""
    await call.message.edit_reply_markup()
    categories = await db.get_list_of_categories_with_items()
    if categories:
        await call.message.answer(f'Выберите категорию, в которой находится товар.',
                                  reply_markup=await generate_keyboard_with_categories(categories))
        await SellerAdmin.EditItemPriceCommand.set()
    else:
        await call.message.answer(f'{error_em} Нет доступных категорий.')
        await state.finish()


@dp.callback_query_handler(text='back', state=SellerAdmin.EditItemPriceProductPriceConfirm)
@dp.callback_query_handler(product_list_data.filter(), state=[SellerAdmin.EditItemPriceCategory,
                                                              SellerAdmin.EditItemPriceProductSizePrice])
async def choose_product(call: CallbackQuery, state: FSMContext, callback_data: dict = None):
    """Админ локации выбирает товар.
    Если у товара нет размеров сразу предлагаем ввести новые цены.
    Если у товара есть размеры предлагаем выбрать размер."""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    if await state.get_state() in ["SellerAdmin:EditItemPriceCategory", "SellerAdmin:EditItemPriceProductSizePrice"]:
        product_id = int(callback_data.get('product_id'))
    else:
        product_id = data.get('product_id')
    category_id = data.get('category_id')
    await state.update_data(product_id=product_id)
    if await db.product_has_size(product_id):
        product_sizes = await db.get_product_sizes_ids_names(product_id)
        await call.message.answer('Выберите размер.',
                                  reply_markup=await generate_keyboard_with_product_sizes(product_sizes, category_id))
        await SellerAdmin.EditItemPriceProduct.set()
    else:
        location_id = await db.get_seller_admin_location(call.from_user.id)
        product_info = await db.get_product_info_prices(product_id, location_id)
        await state.update_data(product_name=product_info["product_name"], location_id=location_id)
        prices = get_price_list(product_info)
        await bot.send_photo(call.from_user.id, photo=product_info['product_photo_id'],
                             caption=f'{product_info["product_name"]}\n'
                                     f'Стоимость:\n'
                                     f'за одну единицу товара: {prices["price_1"]} руб.\n'
                                     f'за две единицы товара: {prices["price_2"]} руб.\n'
                                     f'за три единицы товара: {prices["price_3"]} руб.\n'
                                     f'за четыре единицы товара: {prices["price_4"]} руб.\n'
                                     f'за пять единиц товара: {prices["price_5"]} руб.\n'
                                     f'за шесть и более единиц товара: {prices["price_6"]} руб.\n\n'
                                     f'{attention_em} Чтобы изменить стоимость введите 6 новых цен товара ЧЕРЕЗ '
                                     f'ЗАПЯТУЮ без пробела.\n'
                                     f'Пример:\n'
                                     f"250,240,230,220,210,205",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Назад',
                                         callback_data=categories_data.new(category_id=category_id)
                                     )
                                 ]
                             ]))
        await SellerAdmin.EditItemPriceProductPrice.set()


@dp.message_handler(state=SellerAdmin.EditItemPriceProductPrice)
async def get_new_prices(message: types.Message, state: FSMContext):
    """Получаем список новых цен для товара"""
    new_prices = message.text
    data = await state.get_data()
    category_id = data.get('category_id')
    try:
        list_of_prices = new_prices.split(',')
        prices = {
            'price_1': int(list_of_prices[0]),
            'price_2': int(list_of_prices[1]),
            'price_3': int(list_of_prices[2]),
            'price_4': int(list_of_prices[3]),
            'price_5': int(list_of_prices[4]),
            'price_6': int(list_of_prices[5])
        }
        await state.update_data(prices=prices)
        await message.answer(f"Вы ввели:\n"
                             f"{data['product_name']}\n"
                             f"Цена за 1 шт - {prices['price_1']} руб\n"
                             f"Цена за 2 шт - {prices['price_2']} руб\n"
                             f"Цена за 3 шт - {prices['price_3']} руб\n"
                             f"Цена за 4 шт - {prices['price_4']} руб\n"
                             f"Цена за 5 шт - {prices['price_5']} руб\n"
                             f"Цена за 6 шт - {prices['price_6']} руб\n",
                             reply_markup=confirm_edit_item_price_markup)
        await SellerAdmin.EditItemPriceProductPriceConfirm.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Назад',
                                         callback_data=categories_data.new(category_id=category_id)
                                     )
                                 ]
                             ])
                             )
        await SellerAdmin.EditItemPriceProductPrice.set()


@dp.callback_query_handler(text='save_new_prices', state=SellerAdmin.EditItemPriceProductPriceConfirm)
async def update_item_prices_in_location(call: CallbackQuery, state: FSMContext):
    """ Сохраняем новые цены товара для локации """
    await call.message.edit_reply_markup()
    data = await state.get_data()
    await db.update_product_prices_in_location(data['product_id'], data['location_id'], data['prices'])
    await call.message.answer(f"{success_em} Новые цены успешно установлены!")
    await state.finish()


@dp.callback_query_handler(text='back', state=SellerAdmin.EditItemPriceProductSizePriceConfirm)
@dp.callback_query_handler(size_data.filter(), state=SellerAdmin.EditItemPriceProduct)
async def choose_product_size(call: CallbackQuery, state: FSMContext, callback_data: dict = None):
    """
    Админ локации выбирает размер товара.
    Предлагаем ему ввести новые цены.
    """
    data = await state.get_data()
    if await state.get_state() == "SellerAdmin:EditItemPriceProduct":
        size_id = int(callback_data['size_id'])
    else:
        size_id = data['size_id']
    location_id = await db.get_seller_admin_location(call.from_user.id)
    product_info = await db.get_size_info_prices(size_id, location_id)
    await state.update_data(product_name=product_info["product_name"],
                            location_id=location_id,
                            size_name=product_info['size_name'],
                            size_id=product_info['size_id'])
    prices = get_price_list(product_info)
    await bot.send_photo(call.from_user.id, photo=product_info['product_photo_id'],
                         caption=f'{product_info["product_name"]}\n'
                                 f'Размер: {product_info["size_name"]}\n'
                                 f'Стоимость:\n'
                                 f'за одну единицу товара: {prices["price_1"]} руб.\n'
                                 f'за две единицы товара: {prices["price_2"]} руб.\n'
                                 f'за три единицы товара: {prices["price_3"]} руб.\n'
                                 f'за четыре единицы товара: {prices["price_4"]} руб.\n'
                                 f'за пять единиц товара: {prices["price_5"]} руб.\n'
                                 f'за шесть и более единиц товара: {prices["price_6"]} руб.\n\n'
                                 f'{attention_em} Чтобы изменить стоимость введите 6 новых цен товара ЧЕРЕЗ '
                                 f'ЗАПЯТУЮ без пробела.\n'
                                 f'Пример:\n'
                                 f"250,240,230,220,210,205",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(
                                     text='Назад',
                                     callback_data=product_list_data.new(product_id=data['product_id'])
                                 )
                             ]
                         ]))
    await SellerAdmin.EditItemPriceProductSizePrice.set()


@dp.message_handler(state=SellerAdmin.EditItemPriceProductSizePrice)
async def get_new_size_prices(message: types.Message, state: FSMContext):
    """
    Получаем список новых цен для размера товара
    """
    new_prices = message.text
    data = await state.get_data()
    try:
        list_of_prices = new_prices.split(',')
        size_prices = {
            'price_1': int(list_of_prices[0]),
            'price_2': int(list_of_prices[1]),
            'price_3': int(list_of_prices[2]),
            'price_4': int(list_of_prices[3]),
            'price_5': int(list_of_prices[4]),
            'price_6': int(list_of_prices[5])
        }
        await state.update_data(size_prices=size_prices)
        await message.answer(f"Вы ввели:\n"
                             f"{data['product_name']}\n"
                             f"Размер: {data['size_name']}\n"
                             f"Цена за 1 шт - {size_prices['price_1']} руб\n"
                             f"Цена за 2 шт - {size_prices['price_2']} руб\n"
                             f"Цена за 3 шт - {size_prices['price_3']} руб\n"
                             f"Цена за 4 шт - {size_prices['price_4']} руб\n"
                             f"Цена за 5 шт - {size_prices['price_5']} руб\n"
                             f"Цена за 6 шт - {size_prices['price_6']} руб\n",
                             reply_markup=confirm_edit_item_price_markup)
        await SellerAdmin.EditItemPriceProductSizePriceConfirm.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен размера товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Назад',
                                         callback_data=product_list_data.new(product_id=data['product_id'])
                                     )
                                 ]
                             ])
                             )
        await SellerAdmin.EditItemPriceProductSizePrice.set()


@dp.callback_query_handler(text='save_new_prices', state=SellerAdmin.EditItemPriceProductSizePriceConfirm)
async def update_item_prices_in_location(call: CallbackQuery, state: FSMContext):
    """
    Сохраняем новые цены товара для локации
    """
    await call.message.edit_reply_markup()
    data = await state.get_data()
    await db.update_product_size_prices_in_location(data['size_id'], data['location_id'], data['size_prices'])
    await call.message.answer(f"{success_em} Новые цены успешно установлены!")
    await state.finish()
