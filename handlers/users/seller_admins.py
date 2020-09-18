from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import IsSellerAdminMessage
from keyboards.inline.callback_datas import categories_data
from keyboards.inline.inline_keyboards import cancel_admin_markup, generate_keyboard_with_categories_for_add_item
from loader import dp, db, bot
from states.seller_admin_states import SellerAdmin
from utils.temp_orders_list import get_list_of_sellers_location, get_list_of_couriers_location, \
    get_list_of_category_for_remove_from_stock, get_list_of_category_for_return_to_stock, \
    get_list_of_products_for_remove_from_stock, get_list_of_products_for_return_to_stock


@dp.message_handler(IsSellerAdminMessage(), commands=['add_new_seller'])
async def add_new_seller(message: types.Message, state: FSMContext):
    """Добавление продавца в локацию"""
    location = await db.get_location_by_seller_admin_id(message.from_user.id)
    await state.update_data(location_id=location['admin_seller_location_id'],
                            metro_id=location['admin_seller_metro_id'])
    await message.answer('Введите имя продавца.',
                         reply_markup=cancel_admin_markup)
    await SellerAdmin.SellerName.set()


@dp.message_handler(state=SellerAdmin.SellerName)
async def get_seller_name(message: types.Message, state: FSMContext):
    """ПОлучаем имя продацва"""
    seller_name = message.text
    await state.update_data(seller_name=seller_name)
    await message.answer(f"Отлично!\n"
                         f"Имя продавца - {seller_name}\n"
                         f"Теперь введите id телеграма продавца. Взять id сотрудник может в этом боте @myidbot\n"
                         f"! Внимание! Пользователю будет отправлено сообщение о назначении должности. Поэтому он "
                         f"должен отправить боту хотябы одно сообщение перед назначением.",
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
            await message.answer('Продавец с таким id уже добавлен')
            await state.finish()
    except:
        await message.answer('Не получается добавить пользователя. Возможно он не отправил боту сообщение.'
                             'Попробуйте еще раз.',
                             reply_markup=cancel_admin_markup)
        await SellerAdmin.SellerTelegramID.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_sellers_'])
async def remove_sellers(message: types.Message, state: FSMContext):
    """Удаляем продавца из локации"""
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    await message.answer('Внимание!\n'
                         'Удаление происходит сразу после нажатия на команду')
    sellers_list = await db.get_sellers_list_by_location(location_id)
    print(sellers_list)
    if sellers_list:
        list_message = await get_list_of_sellers_location(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет продавцов в Вашей локации',
                             reply_markup=cancel_admin_markup)
    await SellerAdmin.RemoveSeller.set()


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
            await message.answer('Продавец удален. Чтобы удалить еще одного, снова введите /remove_sellers_')
        else:
            await message.answer('Вы не можете удалить продавца из другой локации')
        await state.finish()
    except:
        await message.answer('Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsSellerAdminMessage(), commands=['add_new_courier'])
async def add_new_courier(message: types.Message, state: FSMContext):
    """Добавление курьера в локацию"""
    location = await db.get_location_by_seller_admin_id(message.from_user.id)
    await state.update_data(location_id=location['admin_seller_location_id'],
                            metro_id=location['admin_seller_metro_id'])
    await message.answer('Введите имя курьера.',
                         reply_markup=cancel_admin_markup)
    await SellerAdmin.CourierName.set()


@dp.message_handler(state=SellerAdmin.CourierName)
async def get_courier_name(message: types.Message, state: FSMContext):
    """ПОлучаем имя курьера"""
    courier_name = message.text
    await state.update_data(courier_name=courier_name)
    await message.answer(f"Отлично!\n"
                         f"Имя курьера - {courier_name}\n"
                         f"Теперь введите id телеграма курьера. Взять id сотрудник может в этом боте @myidbot\n"
                         f"! Внимание! Пользователю будет отправлено сообщение о назначении должности. Поэтому он "
                         f"должен отправить боту хотябы одно сообщение перед назначением.",
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
            await message.answer('Курьер с таким id уже добавлен')
            await state.finish()
    except:
        await message.answer('Не получается добавить пользователя. Возможно он не отправил боту сообщение.'
                             'Попробуйте еще раз.',
                             reply_markup=cancel_admin_markup)
        await SellerAdmin.CourierTelegramID.set()


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_courier_'])
async def remove_courier(message: types.Message, state: FSMContext):
    """Удаляем курьера из локации"""
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    await message.answer('Внимание!\n'
                         'Удаление происходит сразу после нажатия на команду')
    courier_list = await db.get_courier_list_by_location(location_id)
    if courier_list:
        list_message = await get_list_of_couriers_location(courier_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет курьеров в Вашей локации',
                             reply_markup=cancel_admin_markup)
    await SellerAdmin.RemoveCourier.set()


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
            await message.answer('Курьер удален. Чтобы удалить еще одного, снова введите /remove_courier_')
        else:
            await message.answer('Вы не можете удалить курьера из другой локации')
        await state.finish()
    except:
        await message.answer('Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_category_from_stock'])
async def remove_category_from_stock(message: types.Message, state: FSMContext):
    """Убираем категорию из продажи"""
    location_id = await db.get_location_for_seller_admin(message.from_user.id)
    await state.update_data(location_id=location_id)
    category_list = await db.get_categories_in_stock_by_location(location_id, status='true')
    print(category_list)
    if category_list:
        list_message = await get_list_of_category_for_remove_from_stock(category_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет категорий в продаже.',
                             reply_markup=cancel_admin_markup)

    await SellerAdmin.RemoveCategoryFromStock.set()


@dp.message_handler(regexp="remove_from_stock_category_by_id_\d+", state=SellerAdmin.RemoveCategoryFromStock)
async def remove_category_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем категорию с продажи"""
    try:
        data = await state.get_data()
        location_id = data.get('location_id')
        category_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_category_in_location(category_id, location_id)
        await message.answer('Категория снята с продажи\n'
                             ' Чтобы снять еще одну, снова введите /remove_category_from_stock\n'
                             'Чтобы вернуть в продажу, введите /return_category_to_stock')
        await state.finish()
    except:
        await message.answer('Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsSellerAdminMessage(), commands=['return_category_to_stock'])
async def return_category_to_stock(message: types.Message, state: FSMContext):
    """Возвращаем категорию в продажу"""
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


@dp.message_handler(regexp="return_to_stock_category_by_id_\d+", state=SellerAdmin.ReturnCategoryToStock)
async def remove_category_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем категорию с продажи"""
    try:
        data = await state.get_data()
        location_id = data.get('location_id')
        category_id = int(message.text.split('_')[-1])
        await db.return_from_stock_category_in_location(category_id, location_id)
        await message.answer('Категория возвращена в  продажу\n'
                             ' Чтобы вернуть еще одну, снова введите /return_category_to_stock\n'
                             'Чтобы убрать из продажи, введите /remove_category_from_stock')
        await state.finish()
    except:
        await message.answer('Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsSellerAdminMessage(), commands=['remove_item_from_stock'])
async def remove_item_from_stock(message: types.Message, state: FSMContext):
    """Убираем товар из продажу"""
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
                             ' Чтобы снять еще один, снова введите /remove_item_from_stock\n'
                             'Чтобы вернуть в продажу, введите /return_item_to_stock')
        await state.finish()
    except:
        await message.answer('Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsSellerAdminMessage(), commands=['return_item_to_stock'])
async def return_item_to_stock(message: types.Message, state: FSMContext):
    """Возвращаем товар в продажу"""
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
                             ' Чтобы вернуть еще один, снова введите /return_item_to_stock\n'
                             'Чтобы убрать из продажи, введите /remove_item_from_stock')
        await state.finish()
    except:
        await message.answer('Неизвестная команда',
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
                                                 SellerAdmin.ReturnItemToStockProduct])
async def cancel_add_admin(call: CallbackQuery, state: FSMContext):
    """Кнопка отмены"""
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Вы отменили операцию')
