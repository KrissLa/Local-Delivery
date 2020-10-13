import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from filters.users_filters import IsAdminMessage
from keyboards.inline.inline_keyboards import generate_keyboard_with_delivery_categories_for_add_item, \
    cancel_admin_markup, gen_take_order_markup, gen_confirm_order_markup, generate_key_board_with_admins, \
    generate_key_board_with_metro, generate_keyboard_with_categories_for_add_item, generate_delivery_couriers_keyboard
from loader import dp, db
from states.admin_state import AddAdmin
from utils.check_states import states_for_menu, reset_state
from utils.emoji import attention_em_red, attention_em, error_em, warning_em, blue_diamond_em
from utils.product_list import get_delivery_product_list
from utils.temp_orders_list import get_list_of_delivery_category, weekdays, get_list_of_location_message, \
    get_list_of_local_objects, get_list_of_category, get_list_of_seller_admins, get_list_of_sellers, \
    get_list_of_couriers, get_list_of_seller_admins_for_reset, get_list_of_sellers_for_reset, \
    get_list_of_couriers_for_reset, get_list_of_category_for_remove_from_stock, \
    get_list_of_category_for_return_to_stock, get_list_of_seller_admins_for_change, get_list_of_sellers_for_change, \
    get_list_of_couriers_for_change, get_list_of_delivery_couriers


@dp.message_handler(IsAdminMessage(), commands=['edit_delivery_item_price'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['edit_delivery_item_price'])
async def edit_delivery_item_price(message: types.Message, state: FSMContext):
    """Меняем цену товара"""
    await reset_state(state, message)
    category_list = await db.get_delivery_categories_with_products()
    if category_list:
        await message.answer('Выберите категорию, в которой находится товар.',
                             reply_markup=await generate_keyboard_with_delivery_categories_for_add_item(category_list))
    else:
        await message.answer('Пока нет категорий, в которых есть товары',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.EditDeliveryItem.set()


@dp.message_handler(IsAdminMessage(), commands=['return_delivery_item_to_stock'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['return_delivery_item_to_stock'])
async def return_item_to_stock(message: types.Message, state: FSMContext):
    """Возвращаем товар в продажу"""
    await reset_state(state, message)
    category_list = await db.get_category_for_admin_delivery()
    if category_list:
        await message.answer('Выберите категорию, в которой нужно вернуть товар.',
                             reply_markup=await generate_keyboard_with_delivery_categories_for_add_item(category_list))
    else:
        await message.answer('Пока нет категорий, в которых товары сняты с продажи',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ReturnDeliveryItemToStockCategory.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_item_from_stock'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_item_from_stock'])
async def remove_item_from_stock(message: types.Message, state: FSMContext):
    """Убираем товар из продажу"""
    await reset_state(state, message)
    category_list = await db.get_delivery_category_for_remove_item_from_stock()
    if category_list:
        await message.answer('Выберите категорию, из которой нужно убрать товар.',
                             reply_markup=await generate_keyboard_with_delivery_categories_for_add_item(category_list))
    else:
        await message.answer('Пока нет категорий.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveDeliveryItemFromStockCategory.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_item'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_item'])
async def remove_item(message: types.Message, state: FSMContext):
    """Удаление товара"""
    await reset_state(state, message)
    categories = await db.get_list_of_delivery_categories_with_items()
    await message.answer('Выберите категорию, из которой нужно удалить товар',
                         reply_markup=await generate_keyboard_with_delivery_categories_for_add_item(categories))
    await AddAdmin.RemoveDeliveryItemCat.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_category'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_category'])
async def remove_delivery_category(message: types.Message, state: FSMContext):
    """Удаляем категорию"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду.\n'
                         f'{attention_em}Вместе с категорией удаляются все товары в ней')
    category_list = await db.get_delivery_category_list()
    if category_list:
        list_message = await get_list_of_delivery_category(category_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Нет категорий.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveDeliveryCategory.set()


@dp.message_handler(IsAdminMessage(), commands=['take_orders'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['take_orders'])
async def take_orders(message: types.Message, state: FSMContext):
    """Список непринятых или измененных заказов"""
    await reset_state(state, message)
    orders = await db.get_unaccepted_delivery_orders()
    if orders:
        await message.answer('Список непринятых заказов:')
        for order in orders:
            logging.info(order)
            await message.answer(f'{blue_diamond_em} Заказ № {order["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order["delivery_order_id"])}'
                                 f'Сумма заказа: {order["delivery_order_final_price"]} руб.\n'
                                 f'id заказчика - {order["delivery_order_seller_admin_id"]}\n'
                                 f'Адрес доставки: {order["location_name"]}\n'
                                 f'{order["location_address"]}\n'
                                 f'Время создания {order["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                 f'Дата доставки: {order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order["delivery_order_time_info"]}\n'
                                 f'Статус заказа: {order["delivery_order_status"]}\n'
                                 f'{attention_em} Чтобы принять или отклонить нажмите '
                                 f'/take_order_{order["delivery_order_id"]}')
    else:
        await message.answer('Нет непринятых заказов.')


@dp.message_handler(IsAdminMessage(), commands=['delivery_order_set_courier'], state='*')
async def set_courier(message: types.Message, state: FSMContext):
    """Список заказов в которые нужно назначить курьера"""
    await reset_state(state, message)
    orders = await db.get_delivery_orders_for_couriers(message.from_user.id)
    if orders:
        await message.answer('Список заказов, в которых не назначен курьер:')
        for order in orders:
            await message.answer(f'{blue_diamond_em} Заказ № {order["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order["delivery_order_id"])}'
                                 f'Сумма заказа: {order["delivery_order_final_price"]} руб.\n'
                                 f'id заказчика - {order["delivery_order_seller_admin_id"]}\n'
                                 f'Адрес доставки: {order["location_name"]}\n'
                                 f'{order["location_address"]}\n'
                                 f'Время создания {order["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                 f'Дата доставки: {order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order["delivery_order_time_info"]}\n'
                                 f'Статус заказа: {order["delivery_order_status"]}\n'
                                 f'{attention_em} Чтобы назначить курьера нажмите '
                                 f'/delivery_order_set_courier_{order["delivery_order_id"]}')
    else:
        await message.answer('Нет заказов, в которых не назначен курьер.')


@dp.message_handler(IsAdminMessage(), commands=['delivery_orders_awaiting_delivery'], state='*')
async def set_courier(message: types.Message, state: FSMContext):
    """Список заказов в которые нужно назначить курьера"""
    await reset_state(state, message)
    orders = await db.get_delivery_orders_awaiting_delivery(message.from_user.id)
    if orders:
        await message.answer('Список заказов, которые ожидают доставки:')
        for order in orders:
            await message.answer(f'{blue_diamond_em} Заказ № {order["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order["delivery_order_id"])}'
                                 f'Сумма заказа: {order["delivery_order_final_price"]} руб.\n'
                                 f'id заказчика - {order["delivery_order_seller_admin_id"]}\n'
                                 f'Курьер - {order["delivery_courier_name"]}'
                                 f'Адрес доставки: {order["location_name"]}\n'
                                 f'{order["location_address"]}\n'
                                 f'Время создания {order["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                 f'Дата доставки: {order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order["delivery_order_time_info"]}\n'
                                 f'Статус заказа: {order["delivery_order_status"]}\n')
    else:
        await message.answer('Нет заказов, которые ожидают доставки.')


@dp.message_handler(IsAdminMessage(), commands=['delivery_orders_awaiting_courier'], state='*')
async def set_courier(message: types.Message, state: FSMContext):
    """Список заказов в которые нужно назначить курьера"""
    await reset_state(state, message)
    orders = await db.get_delivery_orders_awaiting_courier(message.from_user.id)
    if orders:
        await message.answer('Список заказов, которые ожидают подтверждения от курьера:')
        for order in orders:
            await message.answer(f'{blue_diamond_em} Заказ № {order["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order["delivery_order_id"])}'
                                 f'Сумма заказа: {order["delivery_order_final_price"]} руб.\n'
                                 f'id заказчика - {order["delivery_order_seller_admin_id"]}\n'
                                 f'Адрес доставки: {order["location_name"]}\n'
                                 f'{order["location_address"]}\n'
                                 f'Время создания {order["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                 f'Дата доставки: {order["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order["delivery_order_time_info"]}\n'
                                 f'Статус заказа: {order["delivery_order_status"]}\n')
    else:
        await message.answer('Нет заказов, которые ожидают подтверждения курьера.')


@dp.message_handler(IsAdminMessage(), regexp="delivery_order_set_courier_\d+", state='*')
async def set_courier(message: types.Message, state: FSMContext):
    """set courier"""
    await reset_state(state, message)
    try:
        order_id = int(message.text.split('_')[-1])
        delivery = await db.get_delivery_admin_id(order_id)
        admin_id = await db.get_admin_id(message.from_user.id)
        if delivery['delivery_order_admin_id'] == admin_id and delivery['delivery_order_courier_id'] is None:
            couriers = await db.get_delivery_couriers()
            if couriers:
                order_data = await db.get_delivery_order_data(order_id)
                await message.answer(f'Заказ № {order_data["delivery_order_id"]}\n'
                                     f'{await get_delivery_product_list(order_data["delivery_order_id"])}'
                                     f'Сумма заказа: {order_data["delivery_order_final_price"]} руб.\n'
                                     f'id заказчика - {order_data["delivery_order_seller_admin_id"]}\n'
                                     f'Адрес доставки: {order_data["location_name"]}\n'
                                     f'{order_data["location_address"]}\n'
                                     f'Время создания {order_data["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                     f'Дата доставки: {order_data["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                     f'{weekdays[order_data["delivery_order_day_for_delivery"].weekday()]}\n'
                                     f'Время доставки: {order_data["delivery_order_time_info"]}\n'
                                     f'Статус заказа: {order_data["delivery_order_status"]}\n'
                                     f'{warning_em} Выберите курьера.',
                                     reply_markup=await generate_delivery_couriers_keyboard(couriers, order_id))
                await AddAdmin.SetCourierOrders.set()
        else:
            await message.answer(
                f'Нет заказ с номером № {order_id}, за который отвечаете Вы и в котором не назначен курьер')
    except Exception as err:
        logging.info(err)
        await message.answer('Неизвестная команда')


@dp.message_handler(IsAdminMessage(), regexp="take_order_\d+", state=states_for_menu)
@dp.message_handler(IsAdminMessage(), regexp="take_order_\d+", state='*')
async def take_order__by_id(message: types.Message, state: FSMContext):
    """take_order"""
    await reset_state(state, message)
    try:
        order_id = int(message.text.split('_')[-1])
        if order_id in await db.get_unaccepted_delivery_orders_ids():
            order_data = await db.get_delivery_order_data(order_id)
            await message.answer(f'Заказ № {order_data["delivery_order_id"]}\n'
                                 f'{await get_delivery_product_list(order_data["delivery_order_id"])}'
                                 f'Сумма заказа: {order_data["delivery_order_final_price"]} руб.\n'
                                 f'id заказчика - {order_data["delivery_order_seller_admin_id"]}\n'
                                 f'Адрес доставки: {order_data["location_name"]}\n'
                                 f'{order_data["location_address"]}\n'
                                 f'Время создания {order_data["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                 f'Дата доставки: {order_data["delivery_order_day_for_delivery"].strftime("%d.%m.%Y")} '
                                 f'{weekdays[order_data["delivery_order_day_for_delivery"].weekday()]}\n'
                                 f'Время доставки: {order_data["delivery_order_time_info"]}\n'
                                 f'Статус заказа: {order_data["delivery_order_status"]}\n',
                                 reply_markup=await gen_take_order_markup(order_data["delivery_order_id"]))
            await AddAdmin.TakeOrders.set()
        else:
            await message.answer(f'Нет непринятого или измененного заказ с номером № {order_id}')
    except Exception as err:
        logging.info(err)
        await message.answer('Неизвестная команда')





@dp.message_handler(IsAdminMessage(), commands=['add_delivery_category'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_delivery_category'])
async def add_delivery_category(message: types.Message, state: FSMContext):
    """Добавиление категории"""
    await reset_state(state, message)
    await message.answer('Введите название категории для оптовых поставок',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.DeliveryCategoryName.set()


@dp.message_handler(IsAdminMessage(), commands=['add_delivery_item'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_delivery_item'])
async def add_delivery_item(message: types.Message, state: FSMContext):
    """Добавление товара"""
    await reset_state(state, message)
    categories = await db.get_list_of_delivery_categories()
    if categories:
        await message.answer("Выберите категорию",
                             reply_markup=await generate_keyboard_with_delivery_categories_for_add_item(categories))
        await AddAdmin.DeliveryItemCategory.set()
    else:
        await message.answer("Пока нет категорий. Чтобы добавить нажмите /add_delivery_category")


@dp.message_handler(IsAdminMessage(), commands=['ban_user'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['ban_user'])
async def ban_user(message: types.Message, state: FSMContext):
    """Забанить пользователя"""
    await reset_state(state, message)
    await message.answer('Введите telegramID пользователя',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.BanID.set()


@dp.message_handler(IsAdminMessage(), commands=['unban_user'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['unban_user'])
async def unban_user(message: types.Message, state: FSMContext):
    """Разбан пользователя"""
    await reset_state(state, message)
    await message.answer('Введите telegramID Пользователя',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.UnBanID.set()


@dp.message_handler(IsAdminMessage(), commands=['publish_post'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['publish_post'])
async def publish_post(message: types.Message, state: FSMContext):
    """Создаем промо пост"""
    await reset_state(state, message)
    await message.answer('Загрузите фотографию',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.PromoPhoto.set()


@dp.message_handler(IsAdminMessage(), commands=['set_about'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['set_about'])
async def set_about(message: types.Message, state: FSMContext):
    """Добавить/изменить информацию о компании"""
    await reset_state(state, message)
    await message.answer('Введите информацию о компании',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.SetAbout.set()


@dp.message_handler(IsAdminMessage(), commands=['add_admin'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_admin'])
async def add_admin(message: types.Message, state: FSMContext):
    """Добавляем админа"""
    await reset_state(state, message)
    await message.answer('Пожалуйста, введите имя админа',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.WaitName.set()


@dp.message_handler(IsAdminMessage(), commands=['delete_admin'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['delete_admin'])
async def get_list_admin(message: types.Message, state: FSMContext):
    """Получаем список админов админа"""
    await reset_state(state, message)
    await message.answer('Пожалуйста, выберите админа, которого будем удалять.\n'
                         f'{attention_em_red} Внимание! Удаление происходит сразу после нажатия на кнопку',
                         reply_markup=await generate_key_board_with_admins())
    await AddAdmin.WaitDeleteAdmins.set()


@dp.message_handler(IsAdminMessage(), commands=['add_metro'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_metro'])
async def add_metro(message: types.Message, state: FSMContext):
    """Добавляем ветку метро"""
    await reset_state(state, message)
    await message.answer('Введите название станции метро',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.WaitMetroName.set()


@dp.message_handler(IsAdminMessage(), commands=['delete_metro'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['delete_metro'])
async def delete_metro(message: types.Message, state: FSMContext):
    """Удаляем ветку метро"""
    await reset_state(state, message)
    await message.answer('Выберите станцию метро. \n'
                         f'{attention_em_red}Удаление происходит сразу после нажатия на кнопку.\n'
                         f'{attention_em_red}Вместе с ней удалятся все локации, привязанные к ней.',
                         reply_markup=await generate_key_board_with_metro())
    await AddAdmin.WaitDeleteMetro.set()


@dp.message_handler(IsAdminMessage(), commands=['add_newlocation'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_newlocation'])
async def add_newlocation(message: types.Message, state: FSMContext):
    """Добавляем новую локацию"""
    await reset_state(state, message)
    await message.answer('Выберите ветку метро или введите название новой',
                         reply_markup=await generate_key_board_with_metro())
    await AddAdmin.NewLocationMetro.set()


@dp.message_handler(IsAdminMessage(), commands=['delete_location'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['delete_location'])
async def delete_location(message: types.Message, state: FSMContext):
    """Удаление локации"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} После удаления локации удалятся объекты локальной доставки, '
                         f'привязанные к ней.\n'
                         f'{attention_em} Продавцы и курьеры будут откреплены от точки продаж.\n'
                         f'{attention_em_red} Удаление происходит сразу после нажатия на команду')
    location_list = await db.get_list_of_locations()
    if location_list:
        list_message = await get_list_of_location_message(location_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer("Список локаций пуст",
                             reply_markup=cancel_admin_markup)
    await AddAdmin.DeleteLocation.set()


@dp.message_handler(IsAdminMessage(), commands=['add_local_object'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_local_object'])
async def add_local_object(message: types.Message, state: FSMContext):
    """Добавляем объект локальной доставки"""
    await reset_state(state, message)
    await message.answer("Выберите станцию метро:",
                         reply_markup=await generate_key_board_with_metro())
    await AddAdmin.LocalObjectMetro.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_local_object'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_local_object'])
async def delete_local_object(message: types.Message, state: FSMContext):
    """Удаление бъекта доставки"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду')
    local_objects_list = await db.get_local_objects_list()
    if local_objects_list:
        list_message = await get_list_of_local_objects(local_objects_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Нет объектов локальной доставки',
                             reply_markup=cancel_admin_markup)
    await AddAdmin.RemoveLocalObject.set()


@dp.message_handler(IsAdminMessage(), commands=['add_category'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_category'])
async def add_category(message: types.Message, state: FSMContext):
    """Добавляем категорию"""
    await reset_state(state, message)
    await message.answer('Введите название новой категории',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.NewCategory.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_category'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_category'])
async def remove_category(message: types.Message, state: FSMContext):
    """Удаляем категорию"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду.\n'
                         f'{attention_em}Вместе с категорией удаляются все товары в ней')
    category_list = await db.get_category_list()
    if category_list:
        list_message = await get_list_of_category(category_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Нет категорий.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveCategory.set()


@dp.message_handler(IsAdminMessage(), commands=['add_item'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_item'])
async def add_item(message: types.Message, state: FSMContext):
    """Добавить товар"""
    await reset_state(state, message)
    categories = await db.get_list_of_categories()
    if categories:
        await message.answer("Выберите категорию",
                             reply_markup=await generate_keyboard_with_categories_for_add_item(categories))
        await AddAdmin.ItemCategory.set()
    else:
        await message.answer("Пока нет категорий. Чтобы добавить нажмите /add_category")


@dp.message_handler(IsAdminMessage(), commands=['remove_item'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_item'])
async def remove_item(message: types.Message, state: FSMContext):
    """Удаление товара"""
    await reset_state(state, message)
    categories = await db.get_list_of_categories_with_items()
    if categories:
        await message.answer('Выберите категорию, из которой нужно удалить товар',
                             reply_markup=await generate_keyboard_with_categories_for_add_item(categories))
        await AddAdmin.RemoveItemCategory.set()
    else:
        await message.answer(f'{error_em}Нечего удалять.')


@dp.message_handler(IsAdminMessage(), commands=['add_seller_admin'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_seller_admin'])
async def add_seller_admin(message: types.Message, state: FSMContext):
    """Добавляем админа локации"""
    await reset_state(state, message)
    await message.answer('Пожалуйста, введите имя админа локации',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.AdminSellerName.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_seller_admin'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_seller_admin'])
async def remove_seller_admin(message: types.Message, state: FSMContext):
    """Удаляем админа локации"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду\n')
    sellers_list = await db.get_seller_admins_list()
    if sellers_list:
        list_message = await get_list_of_seller_admins(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет админов локаций.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveSellerAdmin.set()


@dp.message_handler(IsAdminMessage(), commands=['add_seller'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_seller'])
async def add_seller(message: types.Message, state: FSMContext):
    """Добавляем продавца"""
    await reset_state(state, message)
    await message.answer('Пожалуйста, введите имя продавца',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.SellerName.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_seller'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_seller'])
async def remove_seller(message: types.Message, state: FSMContext):
    """Удаляем продавца"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду\n')
    sellers_list = await db.get_seller_list()
    if sellers_list:
        list_message = await get_list_of_sellers(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет продавцов.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveSeller.set()


@dp.message_handler(IsAdminMessage(), commands=['add_courier'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_courier'])
async def add_courier(message: types.Message, state: FSMContext):
    """Добавляем курьера"""
    await reset_state(state, message)
    await message.answer('Пожалуйста, введите имя курьера',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.CourierName.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_courier'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_courier'])
async def remove_courier(message: types.Message, state: FSMContext):
    """Удаляем курьера"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду\n')
    couriers_list = await db.get_courier_list()
    if couriers_list:
        list_message = await get_list_of_couriers(couriers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет курьеров.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveCourier.set()


@dp.message_handler(IsAdminMessage(), commands=['add_delivery_courier'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['add_delivery_courier'])
async def add_courier(message: types.Message, state: FSMContext):
    """Добавляем курьера"""
    await reset_state(state, message)
    await message.answer('Пожалуйста, введите имя курьера',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.DeliveryCourierName.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_courier'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_delivery_courier'])
async def remove_courier(message: types.Message, state: FSMContext):
    """Удаляем курьера"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Удаление происходит сразу после нажатия на команду\n')
    couriers_list = await db.get_delivery_courier_list()
    if couriers_list:
        list_message = await get_list_of_delivery_couriers(couriers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет курьеров.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveDeliveryCourier.set()


@dp.message_handler(IsAdminMessage(), commands=['reset_seller_admin_location'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['reset_seller_admin_location'])
async def reset_seller_admin_location(message: types.Message, state: FSMContext):
    """Сбрасываем локацию у админа локации"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Сбрасывание локации происходит сразу после нажатия на команду\n')
    sellers_list = await db.get_seller_admins_list()
    if sellers_list:
        list_message = await get_list_of_seller_admins_for_reset(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет админов локаций.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ResetSellerAdmin.set()


@dp.message_handler(IsAdminMessage(), commands=['reset_seller_location'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['reset_seller_location'])
async def reset_seller_location(message: types.Message, state: FSMContext):
    """Сбрасываем локацию у продавца"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Сбрасывание локации происходит сразу после нажатия на команду\n')
    sellers_list = await db.get_seller_list()
    if sellers_list:
        list_message = await get_list_of_sellers_for_reset(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет админов локаций.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ResetSeller.set()


@dp.message_handler(IsAdminMessage(), commands=['reset_courier_location'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['reset_courier_location'])
async def reset_courier_location(message: types.Message, state: FSMContext):
    """Сбрасываем локацию у курьера"""
    await reset_state(state, message)
    await message.answer(f'{attention_em_red} Сбрасывание локации происходит сразу после нажатия на команду\n')
    courier_list = await db.get_courier_list()
    if courier_list:
        list_message = await get_list_of_couriers_for_reset(courier_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет курьеров.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ResetCourier.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_category_from_stock'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_category_from_stock'])
async def remove_category_from_stock(message: types.Message, state: FSMContext):
    """Временно снимаем категорию с продажи"""
    await reset_state(state, message)
    category_list = await db.get_category_for_admin_true()
    if category_list:
        list_message = await get_list_of_category_for_remove_from_stock(category_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет категорий в продаже.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveCategoryFromStocks.set()


@dp.message_handler(IsAdminMessage(), commands=['return_category_to_stock'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['return_category_to_stock'])
async def return_category_to_stock(message: types.Message, state: FSMContext):
    """Возвращаем категорию в продажу"""
    await reset_state(state, message)
    category_list = await db.get_category_for_admin_false()
    if category_list:
        list_message = await get_list_of_category_for_return_to_stock(category_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет категорий, снятых с продажи.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ReturnCategoryToStocks.set()


@dp.message_handler(IsAdminMessage(), commands=['remove_item_from_stock'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['remove_item_from_stock'])
async def remove_item_from_stock(message: types.Message, state: FSMContext):
    """Убираем товар из продажу"""
    await reset_state(state, message)
    category_list = await db.get_category_for_remove_item_from_stock()
    if category_list:
        await message.answer('Выберите категорию, из которой нужно убрать товар.',
                             reply_markup=await generate_keyboard_with_categories_for_add_item(category_list))
    else:
        await message.answer('Пока нет категорий.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.RemoveItemFromStockCategory.set()


@dp.message_handler(IsAdminMessage(), commands=['return_item_to_stock'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['return_item_to_stock'])
async def return_item_to_stock(message: types.Message, state: FSMContext):
    """Возвращаем товар в продажу"""
    await reset_state(state, message)
    category_list = await db.get_category_for_admin()
    if category_list:
        await message.answer('Выберите категорию, в которой нужно вернуть товар.',
                             reply_markup=await generate_keyboard_with_categories_for_add_item(category_list))
    else:
        await message.answer('Пока нет категорий, в которых товары сняты с продажи',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ReturnItemToStockCategory.set()


@dp.message_handler(IsAdminMessage(), commands=['change_seller_admin_location'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['change_seller_admin_location'])
async def change_seller_admin_location(message: types.Message, state: FSMContext):
    """Меняем локацию у админа локации"""
    await reset_state(state, message)
    await message.answer('Сначала выберите админа локации')
    sellers_list = await db.get_seller_admins_list()
    if sellers_list:
        list_message = await get_list_of_seller_admins_for_change(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет админов локаций.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ChangeSellerAdmin.set()


@dp.message_handler(IsAdminMessage(), commands=['change_seller_location'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['change_seller_location'])
async def change_seller_location(message: types.Message, state: FSMContext):
    """Меняем локацию у продавца"""
    await reset_state(state, message)
    await message.answer('Сначала выберите продавца')
    sellers_list = await db.get_seller_list()
    if sellers_list:
        list_message = await get_list_of_sellers_for_change(sellers_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет продавцов.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ChangeSeller.set()


@dp.message_handler(IsAdminMessage(), commands=['change_courier_location'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['change_courier_location'])
async def change_courier_location(message: types.Message, state: FSMContext):
    """Меняем локацию у courier"""
    await reset_state(state, message)
    await message.answer('Сначала выберите курьера')
    courier_list = await db.get_courier_list()
    if courier_list:
        list_message = await get_list_of_couriers_for_change(courier_list)
        await message.answer(list_message,
                             reply_markup=cancel_admin_markup)
    else:
        await message.answer('Пока нет курьеров.',
                             reply_markup=cancel_admin_markup)

    await AddAdmin.ChangeCourier.set()


@dp.message_handler(IsAdminMessage(), commands=['edit_metro'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['edit_metro'])
async def edit_metro(message: types.Message, state: FSMContext):
    """Изменяем станцию метро"""
    await reset_state(state, message)
    await message.answer('Сначала выберите станцию метро.',
                         reply_markup=await generate_key_board_with_metro())
    await AddAdmin.EditMetro.set()


@dp.message_handler(IsAdminMessage(), commands=['edit_item'], state=states_for_menu)
@dp.message_handler(IsAdminMessage(), commands=['edit_item'])
async def edit_item(message: types.Message, state: FSMContext):
    """Изменяем товар"""
    await reset_state(state, message)
    categories = await db.get_categories_with_products()
    await message.answer('Выберите категорию, в которой находится товар.',
                         reply_markup=await generate_keyboard_with_categories_for_add_item(categories))
    await AddAdmin.EditItem.set()
