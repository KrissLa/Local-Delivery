import logging
import os

import xlsxwriter
from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.users_filters import IsSellerAdminMessage, SellerAdminHasLocationMessage
from keyboards.inline.inline_keyboards import cancel_admin_markup, generate_keyboard_with_delivery_categories, \
    generate_keyboard_with_none_categories, generate_keyboard_with_categories_for_add_item
from keyboards.inline.statistics_keyboards import period_markup, generate_locations_keyboard_del, \
    generate_delivery_period_keyboard
from loader import dp, db, bot
from states.seller_admin_states import SellerAdmin
from utils.check_states import states_for_menu, reset_state
from utils.emoji import attention_em_red, warning_em, success_em, error_em
from utils.statistics import send_email, send_confirm_mail
from utils.temp_orders_list import get_list_of_delivery_orders, get_list_of_sellers_location, \
    get_list_of_couriers_location, get_list_of_category_for_remove_from_stock, get_list_of_category_for_return_to_stock
from utils.test import generate_table


@dp.message_handler(IsSellerAdminMessage(), commands=['change_delivery_order'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['change_delivery_order'])
async def get_active_delivery_orders(message: types.Message, state: FSMContext):
    """Получаем список активных оптовых заказов"""
    await reset_state(state, message)
    delivery_orders = await db.get_delivery_orders(message.from_user.id)
    if delivery_orders:
        await message.answer(await get_list_of_delivery_orders(delivery_orders),
                             reply_markup=cancel_admin_markup)

    else:
        await message.answer('Нет активных заказов',
                             reply_markup=cancel_admin_markup)
    await SellerAdmin.ChangeOrder.set()


@dp.message_handler(IsSellerAdminMessage(), SellerAdminHasLocationMessage(), commands=['new_delivery_order'],
                    state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), SellerAdminHasLocationMessage(), commands=['new_delivery_order'])
async def add_new_seller(message: types.Message, state: FSMContext):
    """Новый оптовый заказ для производства"""
    logging.info(await state.get_state())
    await reset_state(state, message)
    location_id = await db.get_seller_admin_location(message.from_user.id)
    address_info = await db.get_delivery_address_for_seller_admin(message.from_user.id)
    delivery_order = {
        'address': f'{address_info["metro_name"]}, \n{address_info["location_name"]}, {address_info["location_address"]}',
        'location_id': location_id
    }
    await state.update_data(delivery_order=delivery_order)
    categories = await db.get_delivery_categories()
    if categories:
        markup = await generate_keyboard_with_delivery_categories(categories)
    else:
        markup = await generate_keyboard_with_none_categories()

    await message.answer(f'Создание заказа на поставку.\n'
                         f'Адрес доставки: {delivery_order["address"]}\n'
                         f'Выберите категорию.',
                         reply_markup=markup)
    await SellerAdmin.DeliveryCategory.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['add_new_seller'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['add_new_seller'])
async def add_new_seller(message: types.Message, state: FSMContext):
    """Добавление продавца в локацию"""
    await reset_state(state, message)
    location = await db.get_location_by_seller_admin_id(message.from_user.id)
    await state.update_data(location_id=location['admin_seller_location_id'],
                            metro_id=location['admin_seller_metro_id'])
    await message.answer('Введите имя продавца.',
                         reply_markup=cancel_admin_markup)
    await SellerAdmin.SellerName.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_sellers_'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['remove_sellers_'])
async def remove_sellers(message: types.Message, state: FSMContext):
    """Удаляем продавца из локации"""
    await reset_state(state, message)
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду')
    sellers_list = await db.get_sellers_list_by_location(location_id)
    if sellers_list:
        list_message = await get_list_of_sellers_location(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет продавцов в Вашей локации',
                             reply_markup=cancel_admin_markup)
    await SellerAdmin.RemoveSeller.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['add_new_courier'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['add_new_courier'])
async def add_new_courier(message: types.Message, state: FSMContext):
    """Добавление курьера в локацию"""
    await reset_state(state, message)
    location = await db.get_location_by_seller_admin_id(message.from_user.id)
    await state.update_data(location_id=location['admin_seller_location_id'],
                            metro_id=location['admin_seller_metro_id'])
    await message.answer('Введите имя курьера.',
                         reply_markup=cancel_admin_markup)
    await SellerAdmin.CourierName.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_courier_'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['remove_courier_'])
async def remove_courier(message: types.Message, state: FSMContext):
    """Удаляем курьера из локации"""
    await reset_state(state, message)
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду')
    courier_list = await db.get_courier_list_by_location(location_id)
    if courier_list:
        list_message = await get_list_of_couriers_location(courier_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет курьеров в Вашей локации',
                             reply_markup=cancel_admin_markup)
    await SellerAdmin.RemoveCourier.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_category_from_stock'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['remove_category_from_stock'])
async def remove_category_from_stock(message: types.Message, state: FSMContext):
    """Убираем категорию из продажи"""
    await reset_state(state, message)
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    category_list = await db.get_categories_in_stock_by_location(location_id, status='true')
    if category_list:
        list_message = await get_list_of_category_for_remove_from_stock(category_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет категорий в продаже.',
                             reply_markup=cancel_admin_markup)

    await SellerAdmin.RemoveCategoryFromStock.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['return_category_to_stock'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['return_category_to_stock'])
async def return_category_to_stock(message: types.Message, state: FSMContext):
    """Возвращаем категорию в продажу"""
    await reset_state(state, message)
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    category_list = await db.get_categories_in_stock_by_location(location_id, status='false')
    if category_list:
        list_message = await get_list_of_category_for_return_to_stock(category_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет категорий, снятых с продажи.',
                             reply_markup=cancel_admin_markup)

    await SellerAdmin.ReturnCategoryToStock.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_item_from_stock'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['remove_item_from_stock'])
async def remove_item_from_stock(message: types.Message, state: FSMContext):
    """Убираем товар из продажу"""
    await reset_state(state, message)
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    category_list = await db.get_category_for_stock_item_in_location(location_id, 'true')
    if category_list:
        await message.answer('Выберите категорию, из которой нужно убрать товар.',
                             reply_markup=await generate_keyboard_with_categories_for_add_item(category_list))
    else:
        await message.answer('Пока нет категорий, из которых можно убрать товар.',
                             reply_markup=cancel_admin_markup)

    await SellerAdmin.RemoveItemFromStockCategory.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['return_item_to_stock'], state=states_for_menu)
@dp.message_handler(IsSellerAdminMessage(), commands=['return_item_to_stock'])
async def return_item_to_stock(message: types.Message, state: FSMContext):
    """Возвращаем товар в продажу"""
    await reset_state(state, message)
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    category_list = await db.get_category_for_stock_item_in_location(location_id, 'false')
    if category_list:
        await message.answer('Выберите категорию, в которой нужно вернуть товар.',
                             reply_markup=await generate_keyboard_with_categories_for_add_item(category_list))
    else:
        await message.answer('Пока нет категорий, в которых товары сняты с продажи',
                             reply_markup=cancel_admin_markup)

    await SellerAdmin.ReturnItemToStockCategory.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['update_email'], state='*')
async def get_email(message: types.Message, state: FSMContext):
    """Обновляем email"""
    await reset_state(state, message)
    await message.answer('Пожалуйста, введите email адрес.')
    await SellerAdmin.Email.set()



@dp.message_handler(IsSellerAdminMessage(), SellerAdminHasLocationMessage(), commands=['get_statistics'], state='*')
async def get_statistics(message: types.Message, state: FSMContext):
    """Получить статистику"""
    await reset_state(state, message)
    if await db.get_email_seller(message.from_user.id):
        await message.answer('Выберите период врмени, за который хотите получить статистику',
                             reply_markup=period_markup)
    else:
        await message.answer(
            f'{warning_em} Статистика будет отправлена на email. Чтобы получить статистику Вам сначала нужно ввести'
            ' email адрес - /update_email')


@dp.message_handler(IsSellerAdminMessage(), SellerAdminHasLocationMessage(), commands=['get_delivery_statistics'], state='*')
async def get_statistics(message: types.Message, state: FSMContext):
    """Получить статистику"""
    await reset_state(state, message)
    if await db.get_email_seller(message.from_user.id):
        location_id = await db.get_seller_admin_location(message.from_user.id)
        await message.answer('Выберите локацию, по которой хотите получить статистику',
                             reply_markup=await generate_delivery_period_keyboard(location_id, admin=False))

    else:
        await message.answer(
            f'{warning_em} Статистика будет отправлена на email. Чтобы получить статистику Вам сначала нужно ввести'
            ' email адрес - /update_email')