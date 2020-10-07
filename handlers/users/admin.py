import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentTypes, InlineKeyboardMarkup, InlineKeyboardButton

from filters.users_filters import IsAdminMessage
from keyboards.inline.callback_datas import admin_data, metro_del_data, location_data, categories_data, new_item_size, \
    edit_item_data, edit_item_sizes_data, edit_size_data, take_delivery_order, dont_take_delivery_order, \
    confirm_delivery_order
from keyboards.inline.inline_keyboards import cancel_admin_markup, generate_key_board_with_admins, \
    generate_key_board_with_metro, yes_and_cancel_admin_markup, generate_key_board_with_locations, \
    add_one_more_local_object, add_one_more_category_markup, item_with_size, confirm_item_markup, \
    add_one_more_product_size, generate_keyboard_with_metro_for_seller_admin, \
    get_edit_item_markup, back_button, back_to_choices_sizes, confirm_item_markup_first, \
    gen_take_order_markup, confirm_cancel_delivery
from loader import dp, bot, db
from states.admin_state import AddAdmin
from utils.emoji import attention_em, attention_em_red, error_em, success_em, warning_em
from utils.temp_orders_list import get_sizes, get_list_of_products, get_list_of_products_for_remove_from_stock, \
    get_list_of_products_for_return_to_stock, \
    get_list_of_products_for_edit, get_sizes_for_remove, get_sizes_for_edit, weekdays, get_list_of_delivery_products, \
    get_list_of_delivery_products_for_remove_from_stock, \
    get_list_of_delivery_products_for_return_to_stock, get_list_of_delivery_products_for_edit


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.EditDeliveryItem)
async def get_category_for_return_item_to_stock(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, в которую будем возвращать товар"""
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
async def edit_item_by_id(message: types.Message, state: FSMContext):
    """Меняем цену товара"""
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
async def get_price(message: types.Message, state: FSMContext):
    """Получаем цену"""
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




@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.ReturnDeliveryItemToStockCategory)
async def get_category_for_return_item_to_stock(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, в которую будем возвращать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_delivery_products_for_return_to_stock(category_id)
    if products:
        list_of_products = await get_list_of_delivery_products_for_return_to_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров, снятых с продажи',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.ReturnDeliveryItemToStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="return_delivery_item_to_stock_by_id_\d+",
                    state=AddAdmin.ReturnDeliveryItemToStockProduct)
async def return_item_to_stock_by_id(message: types.Message, state: FSMContext):
    """Возвращаем товар"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.return_to_stock_delivery_item(product_id)
        await message.answer('Товар возвращен в продажу\n'
                             f'{attention_em} Чтобы вернуть еще один снова введите /return_delivery_item_to_stock\n'
                             f'{attention_em} Чтобы убрать из продажи введите /remove_delivery_item_from_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)




@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.RemoveDeliveryItemFromStockCategory)
async def get_category_for_remove_item_from_stock(call: CallbackQuery, callback_data: dict):
    """Получаем категорию из которой будем убирать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_delivery_products_for_remove_from_stock(category_id)
    if products:
        list_of_products = await get_list_of_delivery_products_for_remove_from_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров в продаже',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.RemoveDeliveryItemFromStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_delivery_item_from_stock_by_id_\d+",
                    state=AddAdmin.RemoveDeliveryItemFromStockProduct)
async def remove_item_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем товар с продажи"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_delivery_item(product_id)
        await message.answer('Товар снят с продажи\n'
                             f'{attention_em} Чтобы снять еще один снова введите /remove_delivery_item_from_stock\n'
                             f'{attention_em} Чтобы вернуть в продажу введите /return_delivery_item_to_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


#########
###################


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.RemoveDeliveryItemCat)
async def get_category_for_remove_item(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, из которой нужно удалить товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    list_of_products = await db.get_delivery_products_list(category_id)
    if list_of_products:
        await call.message.answer(f"{attention_em_red} Удаление происходит сразу после нажатия на команду!\n\n"
                                  f"{await get_list_of_delivery_products(list_of_products)}",
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer("В этой категории нет товаров",
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.RemoveDeliveryItem.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_delivery_item_by_id_\d+", state=AddAdmin.RemoveDeliveryItem)
async def remove_item_by_id(message: types.Message, state: FSMContext):
    """Удаляем товар"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.delete_delivery_product_by_id(product_id)
        await message.answer(f'{success_em} Товар удален. \n'
                             f'{attention_em} Чтобы удалить еще один снова введите /remove_delivery_item')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


#######################




@dp.message_handler(IsAdminMessage(), regexp="remove_delivery_category_by_id_\d+",
                    state=AddAdmin.RemoveDeliveryCategory)
async def remove_category_by_id(message: types.Message, state: FSMContext):
    """Удаляем category"""
    try:
        category_id = int(message.text.split('_')[-1])
        await db.delete_delivery_category_by_id(category_id)
        await message.answer(f'{success_em} Категория удалена. \n'
                             f'{attention_em} Чтобы удалить еще одну снова введите /remove_delivery_category')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)



@dp.callback_query_handler(text='back', state=AddAdmin.TakeOrdersWait)
async def back(call: CallbackQuery, state: FSMContext):
    """Назад"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    order_id = data.get('order_id')
    if order_id in await db.get_unaccepted_delivery_orders_ids():
        order_data = await db.get_delivery_order_data(order_id)
        await call.message.answer(f'Заказ № {order_data["delivery_order_id"]}\n'
                                  f'{order_data["delivery_order_info"]}'
                                  f'Сумма заказа: {order_data["delivery_order_price"]} руб.\n'
                                  f'telegramID пользователя - {order_data["delivery_order_user_telegram_id"]}\n'
                                  f'Адрес доставки: {order_data["location_name"]}\n'
                                  f'{order_data["location_address"]}\n'
                                  f'Время создания {order_data["delivery_order_created_at"].strftime("%d.%m.%Y %H:%M")}\n'
                                  f'Дата доставки: {order_data["day_for_delivery"].strftime("%d.%m.%Y")} '
                                  f'{weekdays[order_data["day_for_delivery"].weekday()]}\n'
                                  f'Время доставки: {order_data["delivery_time_info"]}\n'
                                  f'Статус заказа: {order_data["delivery_order_status"]}\n',
                                  reply_markup=await gen_take_order_markup(order_data["delivery_order_id"]))
        await AddAdmin.TakeOrders.set()
    else:
        await call.message.answer(f'Нет непринятого или измененного заказ с номером № {order_id}')


@dp.callback_query_handler(take_delivery_order.filter(), state=AddAdmin.TakeOrders)
async def take_order_confirm(call: CallbackQuery, state: FSMContext, callback_data: dict):
    """Принять заказ"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    status = await db.get_delivery_order_status(order_id)
    if status == 'Ожидание подтверждения':
        await db.update_delivery_order_status(order_id, 'Заказ подтвержден')
    elif status == 'Заказ изменен':
        await db.update_delivery_order_status(order_id, 'Заказ подтвержден после изменения')
    else:
        await call.message.answer(f'{error_em} Что-то пошло не так!')
        await state.finish()
        return
    await call.message.answer(f'{success_em} Заказ № {order_id} принят.\n'
                              f'{warning_em} Подтвердить доставку - /confirm_delivery_{order_id}\n'
                              f'{attention_em} Посмотреть список заказов, которые нужно доставить - '
                              f'/confirm_delivery')
    await state.finish()


@dp.callback_query_handler(dont_take_delivery_order.filter(), state=[AddAdmin.TakeOrders,
                                                                     AddAdmin.ConfirmDeliveryOrders])
async def take_order_cancel(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отклонить заказ заказ"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    await state.update_data(order_id=order_id)
    await call.message.answer("Вы уверены что хотите отклонить заказ?",
                              reply_markup=confirm_cancel_delivery)
    await AddAdmin.TakeOrdersWait.set()


@dp.callback_query_handler(text='confirm_cancel_delivery', state=AddAdmin.TakeOrdersWait)
async def cancel_order(call: CallbackQuery, state: FSMContext):
    """Отменяем заказ"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    order_id = data.get('order_id')
    order_owner = await db.get_delivery_order_owner(order_id)
    await db.update_delivery_order_status(order_id, 'Отменен')
    try:
        await bot.send_message(order_owner, f'{error_em} Ваш заказ на поставку продуктов № {order_id} отменен.')
        await call.message.answer(f'{success_em} Заказ № {order_id} отменен.\n')
    except Exception as err:
        logging.error(err)
        await call.message.answer(f'{success_em} Заказ № {order_id} отменен.\n'
                                  f'{error_em} Не удалось отправить уведомление об отмене админу локации.')

    await state.finish()




@dp.callback_query_handler(confirm_delivery_order.filter(), state=AddAdmin.ConfirmDeliveryOrders)
async def confirm_delivery_orderr(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Подтверждаем доставку заказа"""
    await call.message.edit_reply_markup()
    order_id = int(callback_data.get('order_id'))
    await db.update_delivery_order_status(order_id, 'Заказ доставлен')
    order_owner = await db.get_delivery_order_owner(order_id)
    try:
        await bot.send_message(order_owner, f'{success_em} Ваш заказ на поставку продуктов № {order_id} доставлен.')
        await call.message.answer(f'{success_em} Заказ № {order_id} доставлен.\n')
    except Exception as err:
        logging.error(err)
        await call.message.answer(f'{success_em} Заказ № {order_id} доставлен.\n'
                                  f'{error_em} Не удалось отправить уведомление о доставке админу локации.')
    await state.finish()



@dp.message_handler(state=AddAdmin.DeliveryCategoryName)
async def get_delivery_category_name(message: types.Message, state: FSMContext):
    await db.add_delivery_category(message.text)
    await message.answer(f'{success_em} Новая категория для оптовых поставок добавлена!\n'
                         f'"{message.text}"')
    await state.finish()




@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.DeliveryItemCategory)
async def get_item_category(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id категории"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    category_name = await db.get_delivery_category_name_by_id(category_id)
    new_item = {
        'category_id': category_id,
        'category_name': category_name
    }
    await state.update_data(new_delivery_item=new_item)
    await call.message.answer(f"Вы ввели:\n"
                              f"Категория: {category_name}\n\n"
                              f"Введите название нового товара",
                              reply_markup=cancel_admin_markup)
    await AddAdmin.DeliveryItemName.set()


@dp.message_handler(state=AddAdmin.DeliveryItemName)
async def get_delivery_item_name(message: types.Message, state: FSMContext):
    """Получаем название товара"""
    data = await state.get_data()
    new_delivery_item = data.get('new_delivery_item')
    new_delivery_item['item_name'] = message.text
    await state.update_data(new_delivery_item=new_delivery_item)
    await message.answer(f'Вы ввели:\n'
                         f'Категория: {new_delivery_item["category_name"]}\n'
                         f'Название товара: {new_delivery_item["item_name"]}\n\n'
                         f'{attention_em} Теперь введите цену товара.\n'
                         f'Пример: \n'
                         f'1650',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.DeliveryItemPrice.set()


@dp.message_handler(state=AddAdmin.DeliveryItemPrice)
async def get_delivery_order_price(message: types.Message, state: FSMContext):
    """Получаем цену товара"""
    try:
        price = int(message.text)
        data = await state.get_data()
        new_delivery_item = data.get('new_delivery_item')
        new_delivery_item['price'] = price
        await db.add_delivery_item(new_delivery_item)
        await message.answer(f'{success_em} Новый товар оптовой поставки успешно добавлен!\n\n'
                             f'Категория: {new_delivery_item["category_name"]}\n'
                             f'Название товара: {new_delivery_item["item_name"]}\n'
                             f'Цена за 1 лоток (12шт): {price} руб.')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f"{error_em} Вам нужно ввести число.\n"
                             f'Пример: \n'
                             f'1650',
                             reply_markup=cancel_admin_markup)



@dp.message_handler(state=AddAdmin.BanID)
async def get_ban_id(message: types.Message, state: FSMContext):
    """Получаем id"""
    try:
        ban_id = int(message.text)
        await state.update_data(ban_id=ban_id)
        await message.answer(f'id - {ban_id}\n'
                             f'Теперь введите причину бана.',
                             reply_markup=cancel_admin_markup)
        await AddAdmin.BanReason.set()
    except Exception as err:
        await message.answer(f'{error_em} Не получилось, попробуйте еще раз',
                             reply_markup=cancel_admin_markup)
        await AddAdmin.BanID.set()
        logging.error(err)


@dp.message_handler(state=AddAdmin.BanReason)
async def get_ban_reason(message: types.Message, state: FSMContext):
    """Получаем причину бана"""
    reason = message.text
    data = await state.get_data()
    ban_id = data.get('ban_id')
    try:
        await db.ban_user(ban_id, reason)
        await message.answer('Пользователь забанен.')
    except Exception as err:
        await message.answer(f'{error_em} Не получилось. Попробуйте вручную через базу данных.')
        logging.error(err)
    await state.finish()


@dp.message_handler(state=AddAdmin.UnBanID)
async def get_unban_id(message: types.Message, state: FSMContext):
    """Получаем id"""
    try:
        unban_id = int(message.text)
        try:
            await db.unban_user(unban_id)
            await message.answer('Пользователь разбанен')
        except Exception as err:
            logging.error(err)
            await message.answer(f"{error_em} Не получилось, попробуйте вручную через базу данных")
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f"{error_em} Попробуйте ввести еще раз.",
                             reply_markup=cancel_admin_markup)
        await AddAdmin.UnBanID.set()


@dp.message_handler(state=AddAdmin.PromoPhoto, content_types=ContentTypes.PHOTO)
async def get_promo_photo(message: types.Message, state: FSMContext):
    """Получаем фото"""
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await message.answer('Готово. Теперь введите подпись к фото.',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.PromoCaption.set()


@dp.message_handler(state=[AddAdmin.PromoPhoto])
async def wait_photo(message: types.Message):
    """Ждем фото"""
    await message.answer('Необходимо загрузить фотографию',
                         reply_markup=cancel_admin_markup)


@dp.message_handler(state=AddAdmin.PromoCaption)
async def get_caption(message: types.Message, state: FSMContext):
    """Получаем подпись"""
    caption = message.text
    await state.update_data(caption=caption)
    data = await state.get_data()
    photo_id = data.get('photo_id')
    await message.answer('Вот так будет выглядеть пост:\n\n\n')
    await bot.send_photo(message.from_user.id,
                         photo=photo_id,
                         caption=caption)
    await message.answer('\n\nЧтобы отправить нажмите /send_publish_post',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.PromoConfirm.set()


@dp.message_handler(state=AddAdmin.PromoConfirm, commands=['send_publish_post'])
async def send_publish_post(message: types.Message, state: FSMContext):
    """Отправляем пост"""
    user_list = await db.get_users_id()
    data = await state.get_data()
    photo_id = data.get('photo_id')
    caption = data.get('caption')
    count = 0
    count_error = 0
    for user in user_list:
        try:
            await bot.send_photo(user['user_telegram_id'],
                                 photo=photo_id,
                                 caption=caption)
            count += 1
        except Exception as err:
            logging.error(err)
            count_error += 1
    await message.answer(f'Пост отправлен.\n'
                         f'Успешно - {count} сообщений.\n'
                         f'Ошибок - {count_error}.')
    await state.finish()


@dp.message_handler(state=AddAdmin.SetAbout)
async def get_about(message: types.Message, state: FSMContext):
    """ПОлучаем информацию о компании"""
    about = message.text
    await db.set_about(about)
    await message.answer('Новое описание компании сохранено')
    await state.finish()


@dp.message_handler(state=AddAdmin.WaitName)
async def get_admin_name(message: types.Message, state: FSMContext):
    """Получаем имя админа"""
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Отлично!\n"
                         f"Имя админа - {name}\n"
                         f"Теперь введите id телеграма админа. \n"
                         f"{attention_em}Взять id сотрудник может в этом боте @myidbot\n"
                         f"{attention_em_red} Пользователю будет отправлено сообщение о назначении должности. "
                         f"Поэтому он должен отправить боту хотя бы одно сообщение перед назначением.",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.WaitId.set()


@dp.message_handler(state=AddAdmin.WaitId)
async def get_admin_id(message: types.Message, state: FSMContext):
    """Получаем id админа"""
    try:
        new_id = int(message.text)
        data = await state.get_data()
        name = data.get('name')

        await bot.send_message(new_id, 'Вам назначили должность "Админ"')
        if await db.add_admin(new_id, name):
            await message.answer('Админ успешно добавлен.')
            await state.finish()
        else:
            await message.answer('Админ с таким id уже добавлен')
            await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Не получается добавить пользователя. Возможно, он не отправил боту сообщение.'
                             'Попробуйте еще раз.',
                             reply_markup=cancel_admin_markup)
        await AddAdmin.WaitId.set()


@dp.callback_query_handler(admin_data.filter(), state=AddAdmin.WaitDeleteAdmins)
async def delete_admin(call: CallbackQuery, callback_data: dict):
    """Удаляем админа"""
    admin_id = int(callback_data.get('admin_id'))
    await db.delete_admin(admin_id)
    await call.answer("Админ удален")
    await call.message.edit_reply_markup(await generate_key_board_with_admins())


@dp.message_handler(state=AddAdmin.WaitMetroName)
async def get_metro_name(message: types.Message, state: FSMContext):
    """Сохраняем ветку метро"""
    metro_name = message.text
    await db.add_metro(metro_name)
    await message.answer(f'Станция "{metro_name}" успешно добавлена!')
    await state.finish()


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.WaitDeleteMetro)
async def delete_metro_id(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Удаляем ветку метро"""
    metro_id = int(callback_data.get('metro_id'))
    await db.delete_metro(metro_id)
    await call.message.answer("Станция метро удалена")
    await state.finish()


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.NewLocationMetro)
async def get_metro_id(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Сохоаняем id метро"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    metro_name = await db.get_metro_name_by_id(metro_id)
    new_location = {
        'metro_id': metro_id,
        'metro_name': metro_name
    }
    await state.update_data(new_location=new_location)
    await call.message.answer(f"Теперь введите название локации",
                              reply_markup=cancel_admin_markup)
    await AddAdmin.NewLocationName.set()


@dp.message_handler(state=AddAdmin.NewLocationMetro)
async def get_metro_name(message: types.Message, state: FSMContext):
    """Сохраняем ветку метро"""
    metro_name = message.text
    await db.add_metro(metro_name)
    metro_id = await db.get_last_metro_id()
    new_location = {
        'metro_id': metro_id,
        'metro_name': metro_name
    }
    await state.update_data(new_location=new_location)
    await message.answer(f'Станция "{metro_name}" успешно добавлена!\n'
                         f"Теперь введите название локации",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.NewLocationName.set()


@dp.message_handler(state=AddAdmin.NewLocationName)
async def get_new_location_name(message: types.Message, state: FSMContext):
    """Получаем название новой точки продаж"""
    location_name = message.text
    data = await state.get_data()
    new_location = data.get('new_location')
    new_location["location_name"] = location_name
    await state.update_data(new_location=new_location)
    await message.answer(f'Вы ввели:\n'
                         f'Станция метро - {new_location["metro_name"]}\n'
                         f'Название локации - {new_location["location_name"]}')
    await message.answer('Теперь введите точный адрес локации.',
                         reply_markup=cancel_admin_markup)
    await AddAdmin.NewLocationAddress.set()


@dp.message_handler(state=AddAdmin.NewLocationAddress)
async def get_location_address(message: types.Message, state: FSMContext):
    """"Получаем адрес точки продаж"""
    location_address = message.text
    data = await state.get_data()
    new_location = data.get('new_location')
    new_location['location_address'] = location_address
    await state.update_data(new_location=new_location)
    await message.answer('Вы ввели:\n'
                         f'Станция метро - {new_location["metro_name"]}\n'
                         f'Название локации - {new_location["location_name"]}\n'
                         f'Адрес локации - {new_location["location_address"]}\n'
                         f'Сохраняем?',
                         reply_markup=yes_and_cancel_admin_markup)
    await AddAdmin.SaveNewLocation.set()


@dp.callback_query_handler(text='save_newlocation', state=AddAdmin.SaveNewLocation)
async def save_newlocation(call: CallbackQuery, state: FSMContext):
    """Сохраняем новую локацию"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    new_location = data.get('new_location')
    await db.add_location(new_location)
    await call.message.answer('Новая локация добавлена. \n'
                              f'{attention_em} Чтобы добавить объект локальной доставки '
                              'введите /add_local_object')
    await state.finish()


@dp.message_handler(IsAdminMessage(), regexp="delete_location_\d+", state=AddAdmin.DeleteLocation)
async def delete_location_by_id(message: types.Message, state: FSMContext):
    """Удаляем локацию"""
    try:
        location_id = int(message.text.split('_')[-1])
        await db.delete_location_by_id(location_id)
        await message.answer('Локация удалена. '
                             f'{attention_em} Чтобы удалить еще одну снова введите /delete_location')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer('Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.LocalObjectMetro)
async def get_metro_for_local_object(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Выбираем метро для добавления объекта"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    new_local_object = {
        'metro_id': metro_id
    }
    await state.update_data(new_local_object=new_local_object)

    await call.message.answer(f"Теперь выберите локацию",
                              reply_markup=await generate_key_board_with_locations(metro_id))
    await AddAdmin.LocalObjectLocation.set()


@dp.callback_query_handler(location_data.filter(), state=AddAdmin.LocalObjectLocation)
async def get_location_for_local_object(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Выбираем локацию, в которую добавим объект"""
    await call.message.edit_reply_markup()
    location_id = int(callback_data.get('location_id'))
    location_name = await db.get_location_name_by_id(location_id)
    data = await state.get_data()
    new_local_object = data.get('new_local_object')
    new_local_object['location_id'] = location_id
    new_local_object['location_name'] = location_name
    await state.update_data(new_local_object=new_local_object)
    await call.message.answer("Вы собираетесь добавить объект локальной доставки в локацию \n"
                              f"{location_name}.\n"
                              f"Введите название объекта локальной доставки",
                              reply_markup=cancel_admin_markup)
    await AddAdmin.LocalObjectName.set()


@dp.message_handler(state=AddAdmin.LocalObjectName)
async def get_local_object_name(message: types.Message, state: FSMContext):
    """Получаем название и сразу же сохраняем его"""
    local_object_name = message.text
    data = await state.get_data()
    new_local_object = data.get('new_local_object')
    await db.add_local_object(local_object_name, new_local_object)
    await message.answer(f"Объект локальной доставки {local_object_name} добавлен в локацию \n"
                         f"{new_local_object['location_name']}",
                         reply_markup=add_one_more_local_object)
    await AddAdmin.LocalObjectNameMore.set()


@dp.callback_query_handler(text='add_new_object_done', state=AddAdmin.LocalObjectNameMore)
async def exit_from_add_object(call: CallbackQuery, state: FSMContext):
    """Выходим"""
    await call.message.edit_reply_markup()
    await call.message.answer('Готово. Вы в главном меню')
    await state.finish()


@dp.callback_query_handler(text='one_more_object', state=AddAdmin.LocalObjectNameMore)
async def exit_from_add_object(call: CallbackQuery, state: FSMContext):
    """Добавляем еще один объект"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    new_local_object = data.get('new_local_object')
    await call.message.answer("Вы собираетесь добавить объект доставки в локацию \n"
                              f"{new_local_object['location_name']}.\n"
                              f"Введите название объекта доставки",
                              reply_markup=cancel_admin_markup)
    await AddAdmin.LocalObjectName.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_local_object_\d+", state=AddAdmin.RemoveLocalObject)
async def delete_location_by_id(message: types.Message, state: FSMContext):
    """Удаляем объект доставки"""
    try:
        local_object_id = int(message.text.split('_')[-1])
        await db.delete_local_object_by_id(local_object_id)
        await message.answer('Объект локальной доставки удален. \n'
                             f'{attention_em} Чтобы удалить еще один'
                             ' снова введите /remove_local_object')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer('Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(state=AddAdmin.NewCategory)
async def get_category_name(message: types.Message):
    """Получаем название категории"""
    category_name = message.text
    await db.add_category(category_name)
    await message.answer(f'Категория "{category_name}" добавлена!',
                         reply_markup=add_one_more_category_markup)
    await AddAdmin.OneMoreNewCategory.set()


@dp.callback_query_handler(text='add_new_category_done', state=AddAdmin.OneMoreNewCategory)
async def exit_from_add_category(call: CallbackQuery, state: FSMContext):
    """Выход из добавления категории"""
    await call.message.edit_reply_markup()
    await call.message.answer("Вы завершили добавление категорий")
    await state.finish()


@dp.callback_query_handler(text='one_more_category', state=AddAdmin.OneMoreNewCategory)
async def add_one_more_category(call: CallbackQuery):
    """Добавить еще одну категорию"""
    await call.message.edit_reply_markup()
    await call.message.answer('Введите название новой категории',
                              reply_markup=cancel_admin_markup)
    await AddAdmin.NewCategory.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_category_by_id_\d+", state=AddAdmin.RemoveCategory)
async def remove_category_by_id(message: types.Message, state: FSMContext):
    """Удаляем category"""
    try:
        category_id = int(message.text.split('_')[-1])
        await db.delete_category_by_id(category_id)
        await message.answer('Категория удалена. \n'
                             f'{attention_em} Чтобы удалить еще одну снова введите /remove_category')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.ItemCategory)
async def get_item_category(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id категории"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    category_name = await db.get_category_name_by_id(category_id)
    new_item = {
        'category_id': category_id,
        'category_name': category_name
    }
    await state.update_data(new_item=new_item)
    await call.message.answer(f"Вы ввели:\n"
                              f"Категория: {category_name}\n\n"
                              f"Введите название нового товара",
                              reply_markup=cancel_admin_markup)
    await AddAdmin.ItemName.set()


@dp.message_handler(state=AddAdmin.ItemName)
async def get_item_name(message: types.Message, state: FSMContext):
    """Получаем название товара"""
    item_name = message.text
    data = await state.get_data()
    new_item = data.get('new_item')
    new_item['item_name'] = item_name
    await state.update_data(new_item=new_item)
    await message.answer(f"Вы ввели:\n"
                         f"Категория: {new_item['category_name']}\n"
                         f"Название: {new_item['item_name']}\n\n"
                         f"Добавьте фото товара",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.ItemPhoto.set()


@dp.message_handler(state=AddAdmin.ItemPhoto, content_types=ContentTypes.PHOTO)
async def get_item_photo(message: types.Message, state: FSMContext):
    """Получаем фотографию товара"""
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    new_item = data.get('new_item')
    new_item['photo_id'] = photo_id
    await state.update_data(new_item=new_item)
    await message.answer(f"Вы ввели:\n"
                         f"Категория: {new_item['category_name']}\n"
                         f"Название: {new_item['item_name']}\n"
                         f"Фотография добавлена\n\n"
                         f"Напишите описание товара",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.ItemDescription.set()


@dp.message_handler(state=AddAdmin.ItemDescription)
async def get_item_description(message: types.Message, state: FSMContext):
    """Получаем описание товара"""
    item_description = message.text
    data = await state.get_data()
    new_item = data.get('new_item')
    new_item['item_description'] = item_description
    await state.update_data(new_item=new_item)
    await message.answer(f"Вы ввели:\n"
                         f"Категория: {new_item['category_name']}\n"
                         f"Название: {new_item['item_name']}\n"
                         f"Фотография добавлена\n"
                         f"Описание: {new_item['item_description']}\n\n"
                         f"У товара есть размеры?",
                         reply_markup=item_with_size)
    await AddAdmin.ItemSize.set()


@dp.callback_query_handler(text='back', state=[AddAdmin.ItemSizeNameFirst,
                                               AddAdmin.ItemSizePriceFirst,
                                               AddAdmin.ItemSizeConfirmFirst])
async def back_to_sizes_or_not(call: CallbackQuery, state: FSMContext):
    """Возврат к выбору один размер или несколько"""
    data = await state.get_data()
    product_id = data.get('product_id')
    await db.delete_product_by_id(product_id)
    new_item = data.get('new_item')
    await call.message.answer(f"Вы ввели:\n"
                              f"Категория: {new_item['category_name']}\n"
                              f"Название: {new_item['item_name']}\n"
                              f"Фотография добавлена\n"
                              f"Описание: {new_item['item_description']}\n\n"
                              f"У товара есть размеры?",
                              reply_markup=item_with_size)
    await AddAdmin.ItemSize.set()


# @dp.callback_query_handler(text='cancel', state=[AddAdmin.ItemSizeName,
#                                                AddAdmin.ItemSizePrice,
#                                                AddAdmin.ItemSizeConfirm])
# async def back_to_sizes_or_not(call: CallbackQuery, state: FSMContext):
#     """Возврат к выбору один размер или несколько"""
#     data = await state.get_data()
#     new_item = data.get('new_item')
#     await call.message.answer(f"Вы ввели:\n"
#                               f"Категория: {new_item['category_name']}\n"
#                               f"Название: {new_item['item_name']}\n"
#                               f"Фотография добавлена\n"
#                               f"Описание: {new_item['item_description']}\n\n"
#                               f"У товара есть размеры?",
#                               reply_markup=item_with_size)
#     await AddAdmin.ItemSize.set()


@dp.callback_query_handler(new_item_size.filter(status='True'), state=AddAdmin.ItemSize)
async def item_has_size(call: CallbackQuery, state: FSMContext):
    """У товара есть размеры"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    new_item = data.get('new_item')
    product_id = await db.add_product_with_size(new_item)
    await state.update_data(product_id=product_id)
    await call.message.answer('Вы добавили новый товар.\n'
                              f'Название: {new_item["item_name"]}\n'
                              f'Фото добавлено\n'
                              f'Описание: {new_item["item_description"]}\n\n'
                              f'Введите название размера товара',
                              reply_markup=back_to_choices_sizes)
    await AddAdmin.ItemSizeNameFirst.set()


@dp.message_handler(state=AddAdmin.ItemSizeNameFirst)
async def get_item_size_name(message: types.Message, state: FSMContext):
    """Получаем название размера"""
    size_name = message.text
    await state.update_data(size_name=size_name)
    await message.answer(f'Вы ввели:\n'
                         f'Название размера: {size_name}\n\n'
                         f'Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                         f'Пример:\n'
                         f"250,240,230,220,210,205",
                         reply_markup=back_to_choices_sizes)
    await AddAdmin.ItemSizePriceFirst.set()


@dp.message_handler(state=AddAdmin.ItemSizePriceFirst)
async def get_prices_for_size(message: types.Message, state: FSMContext):
    """Получаем цены"""
    prices = message.text
    try:
        list_of_prices = prices.split(',')
        data = await state.get_data()
        size_name = data.get('size_name')
        size_prices = {
            'price1': int(list_of_prices[0]),
            'price2': int(list_of_prices[1]),
            'price3': int(list_of_prices[2]),
            'price4': int(list_of_prices[3]),
            'price5': int(list_of_prices[4]),
            'price6': int(list_of_prices[5])
        }
        await state.update_data(size_prices=size_prices)
        await message.answer(f"Вы ввели:\n"
                             f"Название размера: {size_name}\n"
                             f"Фотография добавлена\n"
                             f"Цена за 1 шт - {size_prices['price1']} руб\n"
                             f"Цена за 2 шт - {size_prices['price2']} руб\n"
                             f"Цена за 3 шт - {size_prices['price3']} руб\n"
                             f"Цена за 4 шт - {size_prices['price4']} руб\n"
                             f"Цена за 5 шт - {size_prices['price5']} руб\n"
                             f"Цена за 6 шт - {size_prices['price6']} руб\n",
                             reply_markup=confirm_item_markup_first)
        await AddAdmin.ItemSizeConfirmFirst.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205")
        await AddAdmin.ItemSizePriceFirst.set()


@dp.message_handler(state=AddAdmin.ItemSizeName)
async def get_item_size_name(message: types.Message, state: FSMContext):
    """Получаем название размера"""
    size_name = message.text
    await state.update_data(size_name=size_name)
    await message.answer(f'Вы ввели:\n'
                         f'Название размера: {size_name}\n\n'
                         f'Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                         f'Пример:\n'
                         f"250,240,230,220,210,205",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.ItemSizePrice.set()


@dp.message_handler(state=AddAdmin.ItemSizePrice)
async def get_prices_for_size(message: types.Message, state: FSMContext):
    """Получаем цены"""
    prices = message.text
    try:
        list_of_prices = prices.split(',')
        data = await state.get_data()
        size_name = data.get('size_name')
        size_prices = {
            'price1': int(list_of_prices[0]),
            'price2': int(list_of_prices[1]),
            'price3': int(list_of_prices[2]),
            'price4': int(list_of_prices[3]),
            'price5': int(list_of_prices[4]),
            'price6': int(list_of_prices[5])
        }
        await state.update_data(size_prices=size_prices)
        await message.answer(f"Вы ввели:\n"
                             f"Название размера: {size_name}\n"
                             f"Фотография добавлена\n"
                             f"Цена за 1 шт - {size_prices['price1']} руб\n"
                             f"Цена за 2 шт - {size_prices['price2']} руб\n"
                             f"Цена за 3 шт - {size_prices['price3']} руб\n"
                             f"Цена за 4 шт - {size_prices['price4']} руб\n"
                             f"Цена за 5 шт - {size_prices['price5']} руб\n"
                             f"Цена за 6 шт - {size_prices['price6']} руб\n",
                             reply_markup=confirm_item_markup)
        await AddAdmin.ItemSizeConfirm.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205")
        await AddAdmin.ItemSizePrice.set()


@dp.callback_query_handler(text='save_item', state=[AddAdmin.ItemSizeConfirmFirst, AddAdmin.ItemSizeConfirm])
async def save_item_without_size(call: CallbackQuery, state: FSMContext):
    """Сохраняем размер товара"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    size_name = data.get('size_name')
    product_id = data.get('product_id')
    size_prices = data.get('size_prices')
    await db.add_product_size(product_id, size_name, size_prices)
    await state.finish()
    await state.update_data(product_id=product_id)
    await call.message.answer(f"Вы добавили новый размер:\n"
                              f"Название размера: {size_name}\n"
                              f"Цены:\n"
                              f"1 шт = {size_prices['price1']} руб\n"
                              f"2 шт = {size_prices['price2']} руб\n"
                              f"3 шт = {size_prices['price3']} руб\n"
                              f"4 шт = {size_prices['price4']} руб\n"
                              f"5 шт = {size_prices['price5']} руб\n"
                              f"6 шт = {size_prices['price6']} руб\n",
                              reply_markup=add_one_more_product_size)
    await AddAdmin.OneMoreProductSize.set()


@dp.callback_query_handler(state=AddAdmin.OneMoreProductSize, text='one_more_product_size')
async def one_more_product_size(call: CallbackQuery):
    """Добавляем еще один размер"""
    await call.message.edit_reply_markup()
    await call.message.answer('Введите название размера товара',
                              reply_markup=cancel_admin_markup)
    await AddAdmin.ItemSizeName.set()


@dp.callback_query_handler(text='cancel', state=[AddAdmin.ItemSizeName,
                                                 AddAdmin.ItemSizePrice])
@dp.callback_query_handler(state=AddAdmin.OneMoreProductSize, text='add_new_product_size_done')
async def one_more_product_size(call: CallbackQuery, state: FSMContext):
    """Завершаем добавление размеров"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    product_id = data.get('product_id')
    product_info = await db.get_product_info(product_id)
    product_size_list = await db.get_product_sizes(product_id)
    sizes = await get_sizes(product_size_list)
    await bot.send_photo(chat_id=call.from_user.id, photo=product_info['product_photo_id'])
    await call.message.answer(f'Вы добавили новый товар.\n'
                              f'Название: {product_info["product_name"]}\n'
                              f'Описание: {product_info["product_description"]}\n'
                              f'Фото выше\n'
                              f'{sizes}')
    await state.finish()


@dp.callback_query_handler(new_item_size.filter(status='False'), state=AddAdmin.ItemSize)
async def item_has_no_size(call: CallbackQuery, state: FSMContext):
    """У товара нет размеров"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    new_item = data.get('new_item')
    await call.message.answer(f"Вы ввели:\n"
                              f"Категория: {new_item['category_name']}\n"
                              f"Название: {new_item['item_name']}\n"
                              f"Фотография добавлена\n"
                              f"Описание: {new_item['item_description']}\n\n"
                              f'Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                              f'Пример:\n'
                              f"250,240,230,220,210,205",
                              reply_markup=cancel_admin_markup)
    await AddAdmin.ItemPrice.set()


@dp.message_handler(state=AddAdmin.ItemPrice)
async def get_item_price(message: types.Message, state: FSMContext):
    """Получаем цену товара"""
    prices = message.text
    try:
        list_of_prices = prices.split(',')
        data = await state.get_data()
        new_item = data.get('new_item')
        new_item['prices'] = {
            'price1': int(list_of_prices[0]),
            'price2': int(list_of_prices[1]),
            'price3': int(list_of_prices[2]),
            'price4': int(list_of_prices[3]),
            'price5': int(list_of_prices[4]),
            'price6': int(list_of_prices[5])
        }
        await state.update_data(new_item=new_item)
        await message.answer(f"Вы ввели:\n"
                             f"Категория: {new_item['category_name']}\n"
                             f"Название: {new_item['item_name']}\n"
                             f"Фотография добавлена\n"
                             f"Описание: {new_item['item_description']}\n"
                             f"Цена за 1 шт - {new_item['prices']['price1']} руб\n"
                             f"Цена за 2 шт - {new_item['prices']['price2']} руб\n"
                             f"Цена за 3 шт - {new_item['prices']['price3']} руб\n"
                             f"Цена за 4 шт - {new_item['prices']['price4']} руб\n"
                             f"Цена за 5 шт - {new_item['prices']['price5']} руб\n"
                             f"Цена за 6 шт - {new_item['prices']['price6']} руб\n",
                             reply_markup=confirm_item_markup)
        await AddAdmin.ItemConfirm.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205")
        await AddAdmin.ItemPrice.set()


@dp.callback_query_handler(text='save_item', state=AddAdmin.ItemConfirm)
async def save_item_without_size(call: CallbackQuery, state: FSMContext):
    """Сохраняем товар"""
    # await call.message.edit_reply_markup()
    data = await state.get_data()
    new_item = data.get('new_item')
    await db.add_product(new_item)
    await bot.send_photo(call.from_user.id,
                         photo=new_item['photo_id'],
                         caption=f"Готово. Вы добавили новый товар.\n"
                                 f"Название: {new_item['item_name']}\n"
                                 f"Описание: {new_item['item_description']}\n"
                                 f"Цена за 1 шт - {new_item['prices']['price1']} руб\n"
                                 f"Цена за 2 шт - {new_item['prices']['price2']} руб\n"
                                 f"Цена за 3 шт - {new_item['prices']['price3']} руб\n"
                                 f"Цена за 4 шт - {new_item['prices']['price4']} руб\n"
                                 f"Цена за 5 шт - {new_item['prices']['price5']} руб\n"
                                 f"Цена за 6 шт - {new_item['prices']['price6']} руб\n")
    await state.finish()


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.RemoveItemCategory)
async def get_category_for_remove_item(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, из которой нужно удалить товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    list_of_products = await db.get_products_list(category_id)
    if list_of_products:
        await call.message.answer(f"{attention_em_red} Удаление происходит сразу после нажатия на команду!\n\n"
                                  f"{await get_list_of_products(list_of_products)}",
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer("В этой категории нет товаров",
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.RemoveItem.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_item_by_id_\d+", state=AddAdmin.RemoveItem)
async def remove_item_by_id(message: types.Message, state: FSMContext):
    """Удаляем товар"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.delete_product_by_id(product_id)
        await message.answer('Товар удален. \n'
                             f'{attention_em} Чтобы удалить еще один снова введите /remove_item')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(state=AddAdmin.AdminSellerName)
async def get_admin_seller_name(message: types.Message, state: FSMContext):
    """Получаем имя админа локации"""
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Отлично!\n"
                         f"Имя админа локации - {name}\n"
                         f"Теперь введите telegramID админа. \n"
                         f"{attention_em} Взять id сотрудник может в этом боте @myidbot\n"
                         f"{attention_em_red} Пользователю будет отправлено сообщение о назначении должности. "
                         f"Поэтому он должен отправить боту хотя бы одно сообщение перед назначением.",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.AdminSellerID.set()


@dp.message_handler(state=AddAdmin.AdminSellerID)
async def get_admin_seller_id(message: types.Message, state: FSMContext):
    """Получаем id админа"""
    new_id = int(message.text)
    data = await state.get_data()
    name = data.get('name')
    await state.update_data(new_id=new_id)
    await message.answer(f"Отлично!\n"
                         f"Имя админа локации - {name}\n"
                         f"TelegramID - {new_id}\n\n"
                         f"Выберите локацию для закрепления",
                         reply_markup=await generate_keyboard_with_metro_for_seller_admin())
    await AddAdmin.AdminSellerMetro.set()


@dp.callback_query_handler(state=AddAdmin.AdminSellerMetro, text='seller_admin_later')
async def add_seller_admin_without_location(call: CallbackQuery, state: FSMContext):
    """Добавляем админа локации без привязки к локации"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    seller_admin_id = int(data.get('new_id'))
    seller_admin_name = data.get('name')
    if await db.add_seller_admin_without_location(seller_admin_id, seller_admin_name):
        try:
            await bot.send_message('Вам назначена должность "админ локации" пока Вы не закреплены за локацией')
            await call.message.answer(f"{seller_admin_name}\n"
                                      f"Назначен на должность Админ локации.\n"
                                      f"{attention_em} Привязать его к локации Вы можете командой "
                                      f"/change_seller_admin_location")
        except Exception as err:
            logging.error(err)
            await call.message.answer(f"{error_em} Добавил в базу, но не смог отправить ему сообщение. Возможно, он не"
                                      f" написал ничего боту.\n"
                                      f"{seller_admin_name}\n"
                                      f"Назначен на должность Админ локации.\n"
                                      f"{attention_em} Привязать его к локации Вы можете командой "
                                      f"/change_seller_admin_location")
        await state.finish()
    else:
        await call.message.answer(f'{error_em} Админ локации с таким telegramID уже существует.')
        await state.finish()


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.AdminSellerMetro)
async def get_metro_for_admin(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id metro"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    await call.message.answer("Выберите локацию:",
                              reply_markup=await generate_key_board_with_locations(metro_id))
    await AddAdmin.AdminSellerLocation.set()


@dp.callback_query_handler(location_data.filter(), state=AddAdmin.AdminSellerLocation)
async def get_location_for_seller_admin(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем локацию и добавляем админа"""
    await call.message.edit_reply_markup()
    location_id = int(callback_data.get('location_id'))
    location_name = await db.get_location_name_by_id(location_id)
    data = await state.get_data()
    seller_admin_name = data.get('name')
    seller_admin_id = data.get('new_id')
    metro_id = int(data.get('metro_id'))

    if await db.add_seller_admin(seller_admin_id, seller_admin_name, metro_id, location_id):
        try:
            await bot.send_message(seller_admin_id, f'Вам назначена должность "Админ локации" в локации\n'
                                                    f'{location_name}.')
            await call.message.answer(f'{seller_admin_name} назначен админом в локации "{location_name}"')
        except Exception as err:
            logging.error(err)
            await call.message.answer(f'{seller_admin_name} назначен админом в локации "{location_name}"\n'
                                      f"{error_em} Добавил его в таблицу, но не смог отправить ему уведомление"
                                      ". Возможно, он не отправил боту сообщение.\n"
                                      "Вы в главном меню")
        await state.finish()
    else:
        await call.message.answer(f'{error_em} Админ локации с таким telegramID уже существует.')
        await state.finish()


@dp.message_handler(IsAdminMessage(), regexp="remove_seller_admin_by_id_\d+", state=AddAdmin.RemoveSellerAdmin)
async def remove_seller_admin_by_id(message: types.Message, state: FSMContext):
    """Удаляем админа локации"""
    try:
        seller_admin_id = int(message.text.split('_')[-1])
        await db.delete_seller_admin_by_id(seller_admin_id)
        await message.answer('Админ локации удален. \n'
                             f'{attention_em} Чтобы удалить еще одного снова введите /remove_seller_admin')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(state=AddAdmin.SellerName)
async def get_seller_name(message: types.Message, state: FSMContext):
    """Получаем имя продавца"""
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Отлично!\n"
                         f"Имя продавца - {name}\n"
                         f"Теперь введите telegramID продавца. \n"
                         f"{attention_em} Взять id сотрудник может в этом боте @myidbot\n"
                         f"{attention_em_red} Пользователю будет отправлено сообщение о назначении должности. "
                         f"Поэтому он должен отправить боту хотя бы одно сообщение перед назначением.",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.SellerID.set()


@dp.message_handler(state=AddAdmin.SellerID)
async def get_seller_id(message: types.Message, state: FSMContext):
    """Получаем id продавца"""
    new_id = int(message.text)
    data = await state.get_data()
    name = data.get('name')
    await state.update_data(new_id=new_id)
    await message.answer(f"Отлично!\n"
                         f"Имя продавца - {name}\n"
                         f"TelegramID - {new_id}\n\n"
                         f"Выберите локацию для закреплени",
                         reply_markup=await generate_keyboard_with_metro_for_seller_admin())
    await AddAdmin.SellerMetro.set()


@dp.callback_query_handler(state=AddAdmin.SellerMetro, text='seller_admin_later')
async def add_seller_without_location(call: CallbackQuery, state: FSMContext):
    """Добавляем продавца без привязки к локации"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    seller_id = int(data.get('new_id'))
    seller_name = data.get('name')
    if await db.add_seller_without_location(seller_id, seller_name):
        try:
            await bot.send_message('Вам назначена должность "Продавец". Пока Вы не закреплены за локацией')
            await call.message.answer(f"{seller_name}\n"
                                      f"Назначен на должность Продавец.\n"
                                      f"{attention_em} Привязать его к локации Вы можете командой "
                                      f"/change_seller_location")
        except Exception as err:
            logging.error(err)
            await call.message.answer(f"{error_em} Добавил в базу, но не смог отправить ему сообщение. Возможно, он не "
                                      f"написал ничего боту.\n"
                                      f"{seller_name}\n"
                                      f"Назначен на должность Продавец.\n"
                                      f"{attention_em} Привязать его к локации Вы можете командой /change_seller_location")
        await state.finish()
    else:
        await call.message.answer(f'{error_em} Продавец с таким telegramID уже существует.')
        await state.finish()


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.SellerMetro)
async def get_metro_for_seller(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id metro"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    await call.message.answer("Выберите локацию:",
                              reply_markup=await generate_key_board_with_locations(metro_id))
    await AddAdmin.SellerLocation.set()


@dp.callback_query_handler(location_data.filter(), state=AddAdmin.SellerLocation)
async def get_location_for_seller(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем локацию и добавляем Продавца"""
    await call.message.edit_reply_markup()
    location_id = int(callback_data.get('location_id'))
    location_name = await db.get_location_name_by_id(location_id)
    data = await state.get_data()
    seller_name = data.get('name')
    seller_id = data.get('new_id')
    metro_id = int(data.get('metro_id'))

    if await db.add_seller(seller_id, seller_name, metro_id, location_id):
        try:
            await bot.send_message(seller_id, f'Вам назначена должность "Продавец" в локации\n'
                                              f'{location_name}.')
            await call.message.answer(f'{seller_name} назначен продавцом в локации "{location_name}"')
        except Exception as err:
            logging.error(err)
            await call.message.answer(f'{seller_name} назначен продавцом в локации "{location_name}"\n'
                                      f"{error_em} Добавил его в таблицу, но не смог отправить ему уведомление"
                                      ". Возможно, он не отправил боту сообщение.\n"
                                      "Вы в главном меню")
        await state.finish()
    else:
        await call.message.answer(f'{error_em} Продавец с таким telegramID уже существует.')
        await state.finish()


@dp.message_handler(IsAdminMessage(), regexp="remove_seller_by_id_\d+", state=AddAdmin.RemoveSeller)
async def remove_seller_by_id(message: types.Message, state: FSMContext):
    """Удаляем category"""
    try:
        seller_id = int(message.text.split('_')[-1])
        await db.delete_seller_by_id(seller_id)
        await message.answer('Продавец удален. \n'
                             f'{attention_em} Чтобы удалить еще одного снова введите /remove_seller')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(state=AddAdmin.CourierName)
async def get_courier_name(message: types.Message, state: FSMContext):
    """Получаем имя курьера"""
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Отлично!\n"
                         f"Имя курьера - {name}\n"
                         f"Теперь введите telegramID курьера. \n"
                         f"{attention_em} Взять id сотрудник может в этом боте @myidbot\n"
                         f"{attention_em_red} Пользователю будет отправлено сообщение о назначении должности. "
                         f"Поэтому он должен отправить боту хотя бы одно сообщение перед назначением.",
                         reply_markup=cancel_admin_markup)
    await AddAdmin.CourierID.set()


@dp.message_handler(state=AddAdmin.CourierID)
async def get_courier_id(message: types.Message, state: FSMContext):
    """Получаем id курьера"""
    new_id = int(message.text)
    data = await state.get_data()
    name = data.get('name')
    await state.update_data(new_id=new_id)
    await message.answer(f"Отлично!\n"
                         f"Имя курьера - {name}\n"
                         f"TelegramID - {new_id}\n\n"
                         f"Выберите локацию для закреплени",
                         reply_markup=await generate_keyboard_with_metro_for_seller_admin())
    await AddAdmin.CourierMetro.set()


@dp.callback_query_handler(state=AddAdmin.CourierMetro, text='seller_admin_later')
async def add_courier_without_location(call: CallbackQuery, state: FSMContext):
    """Добавляем курьера без привязки к локации"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    courier_id = int(data.get('new_id'))
    courier_name = data.get('name')
    if await db.add_courier_without_location(courier_id, courier_name):
        try:
            await bot.send_message('Вам назначена должность "Курьер". Пока Вы не закреплены за локацией')
            await call.message.answer(f"{courier_name}\n"
                                      f"Назначен на должность Курьер.\n"
                                      f"{attention_em} Привязать его к локации Вы можете командой /change_courier_location")
        except Exception as err:
            logging.error(err)
            await call.message.answer(f"{error_em} Добавил в базу, но не смог отправить ему сообщение. Возможно, он не"
                                      f" написал ничего боту.\n"
                                      f"{courier_name}\n"
                                      f"Назначен на должность Курьер.\n"
                                      f"{attention_em} Привязать его к локации Вы можете командой /change_courier_location")
        await state.finish()
    else:
        await call.message.answer(f'{error_em} Курьер с таким telegramID уже существует.')
        await state.finish()


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.CourierMetro)
async def get_metro_for_courier(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id metro"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    await call.message.answer("Выберите локацию:",
                              reply_markup=await generate_key_board_with_locations(metro_id))
    await AddAdmin.CourierLocation.set()


@dp.callback_query_handler(location_data.filter(), state=AddAdmin.CourierLocation)
async def get_location_for_seller(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем локацию и добавляем Продавца"""
    await call.message.edit_reply_markup()
    location_id = int(callback_data.get('location_id'))
    location_name = await db.get_location_name_by_id(location_id)
    data = await state.get_data()
    courier_name = data.get('name')
    courier_id = data.get('new_id')
    metro_id = int(data.get('metro_id'))

    if await db.add_courier(courier_id, courier_name, metro_id, location_id):
        try:
            await bot.send_message(courier_id, f'Вам назначена должность "Курьер" в локации\n'
                                               f'{location_name}.')
            await call.message.answer(f'{courier_name} назначен продавцом в локации "{location_name}"')
        except Exception as err:
            logging.error(err)
            await call.message.answer(f'{courier_name} назначен продавцом в локации "{location_name}"\n'
                                      f"{error_em} Добавил его в таблицу, но не смог отправить ему уведомление"
                                      ". Возможно, он не отправил боту сообщение.\n"
                                      "Вы в главном меню")
        await state.finish()
    else:
        await call.message.answer(f'{error_em} Курьер с таким telegramID уже существует.')
        await state.finish()


@dp.message_handler(IsAdminMessage(), regexp="remove_courier_by_id_\d+", state=AddAdmin.RemoveCourier)
async def remove_courier_by_id(message: types.Message, state: FSMContext):
    """Удаляем курьера"""
    try:
        courier_id = int(message.text.split('_')[-1])
        await db.delete_courier_by_id(courier_id)
        await message.answer('Курьер удален. \n'
                             f'{attention_em} Чтобы удалить еще одного снова введите /remove_courier')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="reset_seller_admin_by_id_\d+", state=AddAdmin.ResetSellerAdmin)
async def reset_seller_admin_by_id(message: types.Message, state: FSMContext):
    """Сбрасываем локацию админа локации"""
    try:
        seller_admin_id = int(message.text.split('_')[-1])
        await db.reset_seller_admin_by_id(seller_admin_id)
        await message.answer('Админ локации откреплен от локации.\n'
                             f'{attention_em} Чтобы открепить еще одного снова введите /reset_seller_admin_location')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="reset_seller_by_id_\d+", state=AddAdmin.ResetSeller)
async def reset_seller_by_id(message: types.Message, state: FSMContext):
    """Сбрасываем локацию продавца"""
    try:
        seller_id = int(message.text.split('_')[-1])
        await db.reset_seller_by_id(seller_id)
        await message.answer('Продавец откреплен от локации.\n'
                             f'{attention_em} Чтобы открепить еще одного снова введите /reset_seller_location')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="reset_courier_by_id_\d+", state=AddAdmin.ResetCourier)
async def reset_courier_by_id(message: types.Message, state: FSMContext):
    """Сбрасываем локацию курьера"""
    try:
        courier_id = int(message.text.split('_')[-1])
        await db.reset_courier_by_id(courier_id)
        await message.answer('Курьер откреплен от локации.\n'
                             f'{attention_em} Чтобы открепить еще одного снова введите /reset_courier_location')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="remove_from_stock_category_by_id_\d+",
                    state=AddAdmin.RemoveCategoryFromStocks)
async def remove_category_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем категорию с продажи"""
    try:
        category_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_category(category_id)
        await message.answer('Категория снята с продажи\n'
                             f'{attention_em} Чтобы снять еще одну снова введите /remove_category_from_stock\n'
                             f'{attention_em} Чтобы вернуть в продажу введите /return_category_to_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="return_to_stock_category_by_id_\d+",
                    state=AddAdmin.ReturnCategoryToStocks)
async def remove_category_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем категорию с продажи"""
    try:
        category_id = int(message.text.split('_')[-1])
        await db.return_to_stock_category(category_id)
        await message.answer('Категория возвращена в продажу\n'
                             f'{attention_em} Чтобы вернуть еще одну снова введите /return_category_to_stock\n'
                             f'{attention_em} Чтобы убрать из продажи введите /remove_category_from_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.RemoveItemFromStockCategory)
async def get_category_for_remove_item_from_stock(call: CallbackQuery, callback_data: dict):
    """Получаем категорию из которой будем убирать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_products_for_remove_from_stock(category_id)
    if products:
        list_of_products = await get_list_of_products_for_remove_from_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров в продаже',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.RemoveItemFromStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="remove_item_from_stock_by_id_\d+",
                    state=AddAdmin.RemoveItemFromStockProduct)
async def remove_item_from_stock_by_id(message: types.Message, state: FSMContext):
    """Убираем товар с продажи"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.remove_from_stock_item(product_id)
        await message.answer('Товар снят с продажи\n'
                             f'{attention_em} Чтобы снять еще один снова введите /remove_item_from_stock\n'
                             f'{attention_em} Чтобы вернуть в продажу введите /return_item_to_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.ReturnItemToStockCategory)
async def get_category_for_return_item_to_stock(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, в которую будем возвращать товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_products_for_return_to_stock(category_id)
    if products:
        list_of_products = await get_list_of_products_for_return_to_stock(products)
        await call.message.answer(list_of_products,
                                  reply_markup=cancel_admin_markup)
    else:
        await call.message.answer('В этой категории нет товаров, снятых с продажи',
                                  reply_markup=cancel_admin_markup)
    await AddAdmin.ReturnItemToStockProduct.set()


@dp.message_handler(IsAdminMessage(), regexp="return_item_to_stock_by_id_\d+",
                    state=AddAdmin.ReturnItemToStockProduct)
async def return_item_to_stock_by_id(message: types.Message, state: FSMContext):
    """Возвращаем товар"""
    try:
        product_id = int(message.text.split('_')[-1])
        await db.return_to_stock_item(product_id)
        await message.answer('Товар возвращен в продажу\n'
                             f'{attention_em} Чтобы вернуть еще один снова введите /return_item_to_stock\n'
                             f'{attention_em} Чтобы убрать из продажи введите /remove_item_from_stock')
        await state.finish()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.message_handler(IsAdminMessage(), regexp="change_seller_admin_location_by_id_\d+", state=AddAdmin.ChangeSellerAdmin)
async def change_seller_admin_location_by_id(message: types.Message, state: FSMContext):
    """Получаем id админа локации"""
    try:
        seller_admin_id = int(message.text.split('_')[-1])
        await state.update_data(seller_admin_id=seller_admin_id)
        await message.answer('Выберите станцию метро.',
                             reply_markup=await generate_key_board_with_metro())
        await AddAdmin.ChangeSellerAdminMetro.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.ChangeSellerAdminMetro)
async def get_metro_for_change_seller_admin(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id метро"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    await call.message.answer('Теперь выберите локацию',
                              reply_markup=await generate_key_board_with_locations(metro_id))
    await AddAdmin.ChangeSellerAdminLocation.set()


@dp.callback_query_handler(location_data.filter(), state=AddAdmin.ChangeSellerAdminLocation)
async def change_seller_admin_location(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Меняем локацию админу локации"""
    await call.message.edit_reply_markup()
    location_id = int(callback_data.get('location_id'))
    data = await state.get_data()
    metro_id = data.get('metro_id')
    admin_seller_id = data.get('seller_admin_id')
    await db.change_seller_admin_location(admin_seller_id, metro_id, location_id)
    seller_info = await db.get_seller_admin_name_id(admin_seller_id)
    try:
        await bot.send_message(seller_info['admin_seller_telegram_id'],
                               f"Вы перезакреплены в локацию № {location_id}")
    except Exception as err:
        logging.error(err)
        await call.message.answer(f'{error_em} Не далось отправить сообщение админу локации.')
    await call.message.answer(f'{seller_info["admin_seller_name"]} перезакреплен в локацию № {location_id}')
    await state.finish()


@dp.message_handler(IsAdminMessage(), regexp="change_seller_location_by_id_\d+", state=AddAdmin.ChangeSeller)
async def change_seller_location_by_id(message: types.Message, state: FSMContext):
    """Получаем id продавца"""
    try:
        seller_id = int(message.text.split('_')[-1])
        await state.update_data(seller_id=seller_id)
        await message.answer('Выберите станцию метро.',
                             reply_markup=await generate_key_board_with_metro())
        await AddAdmin.ChangeSellerMetro.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.ChangeSellerMetro)
async def get_metro_for_change_seller(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id метро"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    await call.message.answer('Теперь выберите локацию',
                              reply_markup=await generate_key_board_with_locations(metro_id))
    await AddAdmin.ChangeSellerLocation.set()


@dp.callback_query_handler(location_data.filter(), state=AddAdmin.ChangeSellerLocation)
async def change_seller_location(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Меняем локацию продавцу"""
    await call.message.edit_reply_markup()
    location_id = int(callback_data.get('location_id'))
    data = await state.get_data()
    metro_id = data.get('metro_id')
    seller_id = data.get('seller_id')
    await db.change_seller_location(seller_id, metro_id, location_id)
    seller_info = await db.get_seller_name_id(seller_id)
    try:
        await bot.send_message(seller_info['seller_telegram_id'],
                               f"Вы перезакреплены в локацию № {location_id}")
    except Exception as err:
        logging.error(err)
        await call.message.answer(f'{error_em} Не удалось отправить уведомление продавцу.')
    await call.message.answer(f'{seller_info["seller_name"]} перезакреплен в локацию № {location_id}')
    await state.finish()


@dp.message_handler(IsAdminMessage(), regexp="change_courier_location_by_id_\d+", state=AddAdmin.ChangeCourier)
async def change_courier_location_by_id(message: types.Message, state: FSMContext):
    """Получаем id курьера"""
    try:
        courier_id = int(message.text.split('_')[-1])
        await state.update_data(courier_id=courier_id)
        await message.answer('Выберите станцию метро.',
                             reply_markup=await generate_key_board_with_metro())
        await AddAdmin.ChangeCourierMetro.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Неизвестная команда',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.ChangeCourierMetro)
async def get_metro_for_change_courier(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id метро"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    await call.message.answer('Теперь выберите локацию',
                              reply_markup=await generate_key_board_with_locations(metro_id))
    await AddAdmin.ChangeCourierLocation.set()


@dp.callback_query_handler(location_data.filter(), state=AddAdmin.ChangeCourierLocation)
async def change_courier_location(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Меняем локацию курьеру"""
    await call.message.edit_reply_markup()
    location_id = int(callback_data.get('location_id'))
    data = await state.get_data()
    metro_id = data.get('metro_id')
    courier_id = data.get('courier_id')
    await db.change_courier_location(courier_id, metro_id, location_id)
    courier_info = await db.get_courier_name_id(courier_id)
    try:
        await bot.send_message(courier_info['courier_telegram_id'],
                               f"Вы перезакреплены в точку продаж № {location_id}")
    except Exception as err:
        logging.error(err)
        await call.message.answer(f'{error_em} Не удалось отправить уведомление курьеру.')
    await call.message.answer(f'{courier_info["courier_name"]} перезакреплен в локацию № {location_id}')
    await state.finish()


@dp.callback_query_handler(metro_del_data.filter(), state=AddAdmin.EditMetro)
async def get_metro_id(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Получаем id метро"""
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    metro_name = await db.get_metro_name_by_location_metro_id(metro_id)
    await call.message.answer(f'{metro_name}\n'
                              'Введите новое название станции метро:\n',
                              reply_markup=cancel_admin_markup)
    await AddAdmin.EditMetroName.set()


@dp.message_handler(IsAdminMessage(), state=AddAdmin.EditMetroName)
async def get_new_metro_name(message: types.Message, state: FSMContext):
    """ПОлучаем новое название метро"""
    new_metro_name = message.text
    data = await state.get_data()
    metro_id = data.get('metro_id')
    await db.edit_metro_name(metro_id, new_metro_name)
    await message.answer("Название изменено. Теперь станция метро называется:\n"
                         f"{new_metro_name}")
    await state.finish()


@dp.callback_query_handler(categories_data.filter(), state=AddAdmin.EditItem)
async def get_category_id(call: CallbackQuery, callback_data: dict):
    """Получаем категорию, в которой находится товар"""
    await call.message.edit_reply_markup()
    category_id = int(callback_data.get('category_id'))
    products = await db.get_products_list(category_id)
    products_list = await get_list_of_products_for_edit(products)
    await call.message.answer('Выберите товар, который хотите изменить:\n'
                              f'\n{products_list}',
                              reply_markup=cancel_admin_markup)
    await AddAdmin.EditItemById.set()


@dp.message_handler(IsAdminMessage(), regexp="edit_item_by_id_\d+", state=AddAdmin.EditItemById)
async def edit_item_by_id(message: types.Message, state: FSMContext):
    """Получаем товар по id"""
    try:
        product_id = int(message.text.split('_')[-1])
        await state.update_data(product_id=product_id)
        product_info = await db.get_product_info(product_id)
        await message.answer('Вы выбрали:')
        await bot.send_photo(message.from_user.id, photo=product_info['product_photo_id'],
                             caption=f"Название: {product_info['product_name']}\n"
                                     f"Описание: {product_info['product_description']}\n"
                                     f"Цены:\n"
                                     f"1 шт - {product_info['price_1']} руб\n"
                                     f"2 шт - {product_info['price_2']} руб\n"
                                     f"3 шт - {product_info['price_3']} руб\n"
                                     f"4 шт - {product_info['price_4']} руб\n"
                                     f"5 шт - {product_info['price_5']} руб\n"
                                     f"6 шт - {product_info['price_6']} руб\n"
                                     f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                     f"Что будем менять?",
                             reply_markup=await get_edit_item_markup(product_info))
        await AddAdmin.EditItemByWaitSubject.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Не получается отправить информацию о товаре\n'
                             'Если он был добавлен через базу данных, возможно, неправильно '
                             'заполнено поле product_photo_id',
                             reply_markup=cancel_admin_markup)


@dp.callback_query_handler(edit_item_data.filter(subject='name'), state=AddAdmin.EditItemByWaitSubject)
async def edit_item_name(call: CallbackQuery):
    """Меняем название товара"""
    await call.message.edit_reply_markup()
    await call.message.answer('Введите новое название товара',
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemByName.set()


@dp.message_handler(state=AddAdmin.EditItemByName)
async def get_new_item_name(message: types.Message, state: FSMContext):
    """Получаем новое название товара"""
    new_name = message.text
    data = await state.get_data()
    product_id = data.get('product_id')
    await db.edit_product_name(product_id, new_name)
    product_info = await db.get_product_info(product_id)
    await message.answer('Вы выбрали:')
    await bot.send_photo(message.from_user.id, photo=product_info['product_photo_id'],
                         caption=f"Название: {product_info['product_name']}\n"
                                 f"Описание: {product_info['product_description']}\n"
                                 f"Цены:\n"
                                 f"1 шт - {product_info['price_1']} руб\n"
                                 f"2 шт - {product_info['price_2']} руб\n"
                                 f"3 шт - {product_info['price_3']} руб\n"
                                 f"4 шт - {product_info['price_4']} руб\n"
                                 f"5 шт - {product_info['price_5']} руб\n"
                                 f"6 шт - {product_info['price_6']} руб\n"
                                 f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                 f"Вы успешно изменили название товара!\n\n"
                                 f"Что будем менять еще?",
                         reply_markup=await get_edit_item_markup(product_info))
    await AddAdmin.EditItemByWaitSubject.set()


@dp.callback_query_handler(edit_item_data.filter(subject='description'), state=AddAdmin.EditItemByWaitSubject)
async def edit_item_description(call: CallbackQuery):
    """Меняем название товара"""
    await call.message.edit_reply_markup()
    await call.message.answer('Введите новое описание товара',
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemByDescription.set()


@dp.message_handler(state=AddAdmin.EditItemByDescription)
async def get_new_item_description(message: types.Message, state: FSMContext):
    """Получаем новое описание товара"""
    new_description = message.text
    data = await state.get_data()
    product_id = data.get('product_id')
    await db.edit_product_description(product_id, new_description)
    product_info = await db.get_product_info(product_id)
    await message.answer('Вы выбрали:')
    await bot.send_photo(message.from_user.id, photo=product_info['product_photo_id'],
                         caption=f"Название: {product_info['product_name']}\n"
                                 f"Описание: {product_info['product_description']}\n"
                                 f"Цены:\n"
                                 f"1 шт - {product_info['price_1']} руб\n"
                                 f"2 шт - {product_info['price_2']} руб\n"
                                 f"3 шт - {product_info['price_3']} руб\n"
                                 f"4 шт - {product_info['price_4']} руб\n"
                                 f"5 шт - {product_info['price_5']} руб\n"
                                 f"6 шт - {product_info['price_6']} руб\n"
                                 f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                 f"Вы успешно изменили описание товара!\n\n"
                                 f"Что будем менять еще?",
                         reply_markup=await get_edit_item_markup(product_info))
    await AddAdmin.EditItemByWaitSubject.set()


@dp.callback_query_handler(edit_item_data.filter(subject='photo'), state=AddAdmin.EditItemByWaitSubject)
async def edit_item_photo(call: CallbackQuery):
    """Меняем фотографию товара"""
    await call.message.edit_reply_markup()
    await call.message.answer('Загрузите новую фотографию товара',
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemByPhoto.set()


@dp.message_handler(state=AddAdmin.EditItemByPhoto, content_types=ContentTypes.PHOTO)
async def get_new_item_photo(message: types.Message, state: FSMContext):
    """Получаем новую фотографию товара"""
    new_photo_id = message.photo[-1].file_id
    data = await state.get_data()
    product_id = data.get('product_id')
    await db.edit_product_photo(product_id, new_photo_id)
    product_info = await db.get_product_info(product_id)
    await message.answer('Вы выбрали:')
    await bot.send_photo(message.from_user.id, photo=product_info['product_photo_id'],
                         caption=f"Название: {product_info['product_name']}\n"
                                 f"Описание: {product_info['product_description']}\n"
                                 f"Цены:\n"
                                 f"1 шт - {product_info['price_1']} руб\n"
                                 f"2 шт - {product_info['price_2']} руб\n"
                                 f"3 шт - {product_info['price_3']} руб\n"
                                 f"4 шт - {product_info['price_4']} руб\n"
                                 f"5 шт - {product_info['price_5']} руб\n"
                                 f"6 шт - {product_info['price_6']} руб\n"
                                 f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                 f"Вы успешно изменили фотографию товара!\n\n"
                                 f"Что будем менять еще?",
                         reply_markup=await get_edit_item_markup(product_info))
    await AddAdmin.EditItemByWaitSubject.set()


@dp.callback_query_handler(edit_item_data.filter(subject='prices'), state=AddAdmin.EditItemByWaitSubject)
async def edit_item_prices(call: CallbackQuery):
    """Меняем цены товара"""
    await call.message.edit_reply_markup()
    await call.message.answer(f'Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                              f'Пример:\n'
                              f"250,240,230,220,210,205",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemByPrices.set()


@dp.message_handler(state=AddAdmin.EditItemByPrices)
async def get_new_item_prices(message: types.Message, state: FSMContext):
    """Получаем новые цены товара"""
    prices = message.text
    try:
        list_of_prices = prices.split(',')
        prices = {
            'price1': int(list_of_prices[0]),
            'price2': int(list_of_prices[1]),
            'price3': int(list_of_prices[2]),
            'price4': int(list_of_prices[3]),
            'price5': int(list_of_prices[4]),
            'price6': int(list_of_prices[5])
        }
        data = await state.get_data()
        product_id = data.get('product_id')
        await db.edit_product_prices(product_id, prices)
        product_info = await db.get_product_info(product_id)
        await message.answer('Вы выбрали:')
        await bot.send_photo(message.from_user.id, photo=product_info['product_photo_id'],
                             caption=f"Название: {product_info['product_name']}\n"
                                     f"Описание: {product_info['product_description']}\n"
                                     f"Цены:\n"
                                     f"1 шт - {product_info['price_1']} руб\n"
                                     f"2 шт - {product_info['price_2']} руб\n"
                                     f"3 шт - {product_info['price_3']} руб\n"
                                     f"4 шт - {product_info['price_4']} руб\n"
                                     f"5 шт - {product_info['price_5']} руб\n"
                                     f"6 шт - {product_info['price_6']} руб\n"
                                     f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                     f"Вы успешно изменили цены товара!\n\n"
                                     f"Что будем менять еще?",
                             reply_markup=await get_edit_item_markup(product_info))
        await AddAdmin.EditItemByWaitSubject.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     back_button
                                 ]
                             ]))
        await AddAdmin.EditItemByPrices.set()


@dp.callback_query_handler(edit_item_data.filter(subject='available'), state=AddAdmin.EditItemByWaitSubject)
async def edit_item_available(call: CallbackQuery, callback_data: dict):
    """Меняем наличие в продаже товара"""
    await call.message.edit_reply_markup()
    item_id = int(callback_data.get('item_id'))
    is_available = await db.item_is_available(item_id)
    if is_available:
        await call.message.answer('Товар сейчас в продаже.\n'
                                  'Хотите убрать?',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text="Убрать из продажи",
                                              callback_data='edit_remove_item_from_stock'
                                          )
                                      ],
                                      [
                                          back_button
                                      ]
                                  ]))
    else:
        await call.message.answer('Товар сейчас снят с продажи.\n'
                                  'Хотите вернуть?',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text="Вернуть в продажу",
                                              callback_data='edit_return_item_to_stock'
                                          )
                                      ],
                                      [
                                          back_button
                                      ]
                                  ]))
    await AddAdmin.EditItemByAvailability.set()


@dp.callback_query_handler(text='edit_remove_item_from_stock', state=AddAdmin.EditItemByAvailability)
async def edit_remove_item_from_stock(call: CallbackQuery, state: FSMContext):
    """Снимаем товар с продажи"""
    data = await state.get_data()
    product_id = data.get('product_id')
    await db.remove_from_stock_item(product_id)
    product_info = await db.get_product_info(product_id)
    await call.message.answer('Вы выбрали:')
    await bot.send_photo(call.from_user.id, photo=product_info['product_photo_id'],
                         caption=f"Название: {product_info['product_name']}\n"
                                 f"Описание: {product_info['product_description']}\n"
                                 f"Цены:\n"
                                 f"1 шт - {product_info['price_1']} руб\n"
                                 f"2 шт - {product_info['price_2']} руб\n"
                                 f"3 шт - {product_info['price_3']} руб\n"
                                 f"4 шт - {product_info['price_4']} руб\n"
                                 f"5 шт - {product_info['price_5']} руб\n"
                                 f"6 шт - {product_info['price_6']} руб\n"
                                 f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                 f"Вы успешно изменили наличие в продаже товара!\n\n"
                                 f"Что будем менять еще?",
                         reply_markup=await get_edit_item_markup(product_info))
    await AddAdmin.EditItemByWaitSubject.set()


@dp.callback_query_handler(text='edit_return_item_to_stock', state=AddAdmin.EditItemByAvailability)
async def edit_remove_item_from_stock(call: CallbackQuery, state: FSMContext):
    """Снимаем товар с продажи"""
    data = await state.get_data()
    product_id = data.get('product_id')
    await db.return_to_stock_item(product_id)
    product_info = await db.get_product_info(product_id)
    await call.message.answer('Вы выбрали:')
    await bot.send_photo(call.from_user.id, photo=product_info['product_photo_id'],
                         caption=f"Название: {product_info['product_name']}\n"
                                 f"Описание: {product_info['product_description']}\n"
                                 f"Цены:\n"
                                 f"1 шт - {product_info['price_1']} руб\n"
                                 f"2 шт - {product_info['price_2']} руб\n"
                                 f"3 шт - {product_info['price_3']} руб\n"
                                 f"4 шт - {product_info['price_4']} руб\n"
                                 f"5 шт - {product_info['price_5']} руб\n"
                                 f"6 шт - {product_info['price_6']} руб\n"
                                 f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                 f"Вы успешно изменили наличие в продаже товара!\n\n"
                                 f"Что будем менять еще?",
                         reply_markup=await get_edit_item_markup(product_info))
    await AddAdmin.EditItemByWaitSubject.set()


@dp.callback_query_handler(edit_item_data.filter(subject='sizes'), state=AddAdmin.EditItemByWaitSubject)
async def edit_item_sizes(call: CallbackQuery, state: FSMContext):
    """Меняем размеры товара"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item_id = data.get('product_id')
    item_has_sizes = await db.product_has_size(item_id)
    if item_has_sizes:
        sizes = await db.get_product_sizes(item_id)
        list_of_sizes = await get_sizes(sizes)
        await call.message.answer('У товара есть размеры:\n'
                                  f'{list_of_sizes}\n\n'
                                  f'Выберите действие:',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text="Добавить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='add_size')
                                          )
                                      ],
                                      [
                                          InlineKeyboardButton(
                                              text="Удалить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='remove_size')
                                          )
                                      ],
                                      [
                                          InlineKeyboardButton(
                                              text="Изменить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='edit_size')
                                          )
                                      ],
                                      [
                                          back_button
                                      ]
                                  ]))
    else:
        await call.message.answer('У товара нет размеров.\n'
                                  'Выберите действие:',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text="Добавить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='add_size')
                                          )
                                      ],
                                      [
                                          back_button
                                      ]
                                  ]))
    await AddAdmin.EditItemBySizes.set()


@dp.callback_query_handler(edit_item_sizes_data.filter(subject='add_size'), state=AddAdmin.EditItemBySizes)
async def add_item_size(call: CallbackQuery):
    """Добавляем размер"""
    await call.message.edit_reply_markup()
    await call.message.answer("Введите название размера",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemNewSizeName.set()


@dp.message_handler(state=AddAdmin.EditItemNewSizeName)
async def get_new_size_name(message: types.Message, state: FSMContext):
    """Получаем название размера"""
    new_size_name = message.text
    await state.update_data(new_size_name=new_size_name)
    await message.answer(f"Название размера: {new_size_name}.\n"
                         f'Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                         f'Пример:\n'
                         f"250,240,230,220,210,205",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(
                                     text='Назад к выбору действия',
                                     callback_data='back'
                                 )
                             ]
                         ])
                         )
    await AddAdmin.EditItemNewSizePrices.set()


@dp.message_handler(state=AddAdmin.EditItemNewSizePrices)
async def get_prices_for_new_size(message: types.Message, state: FSMContext):
    """Получаем список цен"""
    prices = message.text
    try:
        list_of_prices = prices.split(',')
        prices = {
            'price1': int(list_of_prices[0]),
            'price2': int(list_of_prices[1]),
            'price3': int(list_of_prices[2]),
            'price4': int(list_of_prices[3]),
            'price5': int(list_of_prices[4]),
            'price6': int(list_of_prices[5])
        }
        data = await state.get_data()
        item_id = data.get('product_id')
        size_name = data.get('new_size_name')
        await db.add_product_size(item_id, size_name, prices)
        item_has_sizes = await db.product_has_size(item_id)
        if item_has_sizes:
            sizes = await db.get_product_sizes(item_id)
            list_of_sizes = await get_sizes(sizes)
            await message.answer('У товара есть размеры:\n'
                                 f'{list_of_sizes}\n\n'
                                 f'Новый размер успешно добавлен!\n'
                                 f'Выберите действие:',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text="Добавить размер",
                                             callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                    subject='add_size')
                                         )
                                     ],
                                     [
                                         InlineKeyboardButton(
                                             text="Удалить размер",
                                             callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                    subject='remove_size')
                                         )
                                     ],
                                     [
                                         InlineKeyboardButton(
                                             text="Изменить размер",
                                             callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                    subject='edit_size')
                                         )
                                     ],
                                     [
                                         back_button
                                     ]
                                 ]))
        else:
            await message.answer('У товара нет размеров.\n'
                                 'Выберите действие:',
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text="Добавить размер",
                                             callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                    subject='add_size')
                                         )
                                     ],
                                     [
                                         back_button
                                     ]
                                 ]))
        await AddAdmin.EditItemBySizes.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     back_button
                                 ]
                             ]))
        await AddAdmin.EditItemNewSizePrices.set()


@dp.callback_query_handler(edit_item_sizes_data.filter(subject='remove_size'), state=AddAdmin.EditItemBySizes)
async def remove_item_size(call: CallbackQuery, callback_data: dict):
    """Удаляем размер"""
    await call.message.edit_reply_markup()
    item_id = int(callback_data.get('item_id'))
    sizes = await db.get_product_sizes(item_id)
    list_of_sizes = await get_sizes_for_remove(sizes)
    await call.message.answer("Выберите размер, который нужно удалить.\n"
                              f"{attention_em_red} размер удаляется сразу после нажатия на команду\n"
                              f"{list_of_sizes}",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemRemoveSizes.set()


@dp.message_handler(state=AddAdmin.EditItemRemoveSizes, regexp="remove_size_by_id_\d+")
async def remove_size_by_id(message: types.Message, state: FSMContext):
    """Удаляем размер по id"""
    size_id = int(message.text.split('_')[-1])
    data = await state.get_data()
    item_id = data.get('product_id')
    await db.remove_size_by_id(size_id)
    item_has_sizes = await db.product_has_size(item_id)
    if item_has_sizes:
        sizes = await db.get_product_sizes(item_id)
        list_of_sizes = await get_sizes(sizes)
        await message.answer('У товара есть размеры:\n'
                             f'{list_of_sizes}\n\n'
                             f'Размер успешно удален\n'
                             f'Выберите действие:',
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text="Добавить размер",
                                         callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                subject='add_size')
                                     )
                                 ],
                                 [
                                     InlineKeyboardButton(
                                         text="Удалить размер",
                                         callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                subject='remove_size')
                                     )
                                 ],
                                 [
                                     InlineKeyboardButton(
                                         text="Изменить размер",
                                         callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                subject='edit_size')
                                     )
                                 ],
                                 [
                                     back_button
                                 ]
                             ]))
    else:
        await message.answer('У товара нет размеров.\n'
                             f'Размер успешно удален\n'
                             'Выберите действие:',
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text="Добавить размер",
                                         callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                subject='add_size')
                                     )
                                 ],
                                 [
                                     back_button
                                 ]
                             ]))
    await AddAdmin.EditItemBySizes.set()


@dp.callback_query_handler(edit_item_sizes_data.filter(subject='edit_size'), state=AddAdmin.EditItemBySizes)
async def edit_item_size(call: CallbackQuery, callback_data: dict):
    """Удаляем размер"""
    await call.message.edit_reply_markup()
    item_id = int(callback_data.get('item_id'))
    sizes = await db.get_product_sizes(item_id)
    list_of_sizes = await get_sizes_for_edit(sizes)
    await call.message.answer("Выберите размер, который нужно изменить.\n"
                              f"{list_of_sizes}",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemEditSizes.set()


@dp.message_handler(state=AddAdmin.EditItemEditSizes, regexp="edit_size_by_id_\d+")
async def edit_size_by_id(message: types.Message, state: FSMContext):
    """Изменяем размер по id"""
    size_id = int(message.text.split('_')[-1])
    await state.update_data(size_id=size_id)

    size_info = await db.get_size_info_by_id(size_id)
    await state.update_data(size_name=size_info['size_name'])
    await message.answer(f"Название размера: {size_info['size_name']}\n"
                         f"Цены:\n"
                         f"1 шт - {size_info['price_1']} руб\n"
                         f"2 шт - {size_info['price_2']} руб\n"
                         f"3 шт - {size_info['price_3']} руб\n"
                         f"4 шт - {size_info['price_4']} руб\n"
                         f"5 шт - {size_info['price_5']} руб\n"
                         f"6 шт - {size_info['price_6']} руб\n\n"
                         f"Что будем менять?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(
                                     text='Название',
                                     callback_data=edit_size_data.new(size_id=size_id,
                                                                      subject='name')
                                 )
                             ],
                             [
                                 InlineKeyboardButton(
                                     text='Цены',
                                     callback_data=edit_size_data.new(size_id=size_id,
                                                                      subject='price')
                                 )
                             ],
                             [
                                 back_button
                             ]
                         ]))
    await AddAdmin.EditItemEditSizeById.set()


@dp.callback_query_handler(edit_size_data.filter(subject='name'), state=AddAdmin.EditItemEditSizeById)
async def edit_size_name(call: CallbackQuery, state: FSMContext):
    """Меняем имя размера"""
    data = await state.get_data()
    size_name = data.get('size_name')
    await call.message.answer(f'Название размера - {size_name}\n'
                              f'Введите новое название размера.',
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='Назад',
                                          callback_data='back'
                                      )
                                  ]
                              ]))
    await AddAdmin.EditItemEditSizeByIdName.set()


@dp.message_handler(state=AddAdmin.EditItemEditSizeByIdName)
async def get_new_size_name(message: types.Message, state: FSMContext):
    """Получаем новое название размера"""
    data = await state.get_data()
    new_name = message.text
    await state.update_data(size_name=new_name)
    size_id = data.get('size_id')
    await db.edit_size_name(size_id, new_name)
    size_info = await db.get_size_info_by_id(size_id)
    await state.update_data(size_name=size_info['size_name'])
    await message.answer(f"Название размера успешно изменено!\n"
                         f"Название размера: {size_info['size_name']}\n"
                         f"Цены:\n"
                         f"1 шт - {size_info['price_1']} руб\n"
                         f"2 шт - {size_info['price_2']} руб\n"
                         f"3 шт - {size_info['price_3']} руб\n"
                         f"4 шт - {size_info['price_4']} руб\n"
                         f"5 шт - {size_info['price_5']} руб\n"
                         f"6 шт - {size_info['price_6']} руб\n\n"
                         f"Что будем менять?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(
                                     text='Название',
                                     callback_data=edit_size_data.new(size_id=size_id,
                                                                      subject='name')
                                 )
                             ],
                             [
                                 InlineKeyboardButton(
                                     text='Цены',
                                     callback_data=edit_size_data.new(size_id=size_id,
                                                                      subject='price')
                                 )
                             ],
                             [
                                 back_button
                             ]
                         ]))
    await AddAdmin.EditItemEditSizeById.set()


@dp.callback_query_handler(edit_size_data.filter(subject='price'), state=AddAdmin.EditItemEditSizeById)
async def edit_size_prices(call: CallbackQuery, state: FSMContext):
    """Меняем цены размера"""
    data = await state.get_data()
    size_name = data.get('size_name')
    await call.message.answer(f'Название размера - {size_name}\n'
                              f'Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                              f'Пример:\n'
                              f"250,240,230,220,210,205",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='Назад',
                                          callback_data='back'
                                      )
                                  ]
                              ]))
    await AddAdmin.EditItemEditSizeByIdPrices.set()


@dp.message_handler(state=AddAdmin.EditItemEditSizeByIdPrices)
async def get_new_size_prices(message: types.Message, state: FSMContext):
    """ПОлучаем новые цены"""
    prices = message.text
    try:
        list_of_prices = prices.split(',')
        prices = {
            'price1': int(list_of_prices[0]),
            'price2': int(list_of_prices[1]),
            'price3': int(list_of_prices[2]),
            'price4': int(list_of_prices[3]),
            'price5': int(list_of_prices[4]),
            'price6': int(list_of_prices[5])
        }
        data = await state.get_data()
        size_id = data.get('size_id')
        await db.edit_size_prices(size_id, prices)
        size_info = await db.get_size_info_by_id(size_id)
        await message.answer(f"Цены размера успешно изменены!\n"
                             f"Название размера: {size_info['size_name']}\n"
                             f"Цены:\n"
                             f"1 шт - {size_info['price_1']} руб\n"
                             f"2 шт - {size_info['price_2']} руб\n"
                             f"3 шт - {size_info['price_3']} руб\n"
                             f"4 шт - {size_info['price_4']} руб\n"
                             f"5 шт - {size_info['price_5']} руб\n"
                             f"6 шт - {size_info['price_6']} руб\n\n"
                             f"Что будем менять?",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Название',
                                         callback_data=edit_size_data.new(size_id=size_id,
                                                                          subject='name')
                                     )
                                 ],
                                 [
                                     InlineKeyboardButton(
                                         text='Цены',
                                         callback_data=edit_size_data.new(size_id=size_id,
                                                                          subject='price')
                                     )
                                 ],
                                 [
                                     back_button
                                 ]
                             ]))
        await AddAdmin.EditItemEditSizeById.set()
    except Exception as err:
        logging.error(err)
        await message.answer(f'{error_em} Введите 6 новых цен товара ЧЕРЕЗ ЗАПЯТУЮ\n'
                             f'Пример:\n'
                             f"250,240,230,220,210,205",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     back_button
                                 ]
                             ]))
        await AddAdmin.EditItemEditSizeByIdPrices.set()


#############################################
@dp.callback_query_handler(text='back', state=[AddAdmin.EditItemEditSizeByIdName,
                                               AddAdmin.EditItemEditSizeByIdPrices])
async def back_to_size(call: CallbackQuery, state: FSMContext):
    """Назад к размеру"""
    data = await state.get_data()
    size_id = data.get('size_id')
    size_info = await db.get_size_info_by_id(size_id)
    await state.update_data(size_name=size_info['size_name'])
    await call.message.answer(f"Название размера: {size_info['size_name']}\n"
                              f"Цены:\n"
                              f"1 шт - {size_info['price_1']} руб\n"
                              f"2 шт - {size_info['price_2']} руб\n"
                              f"3 шт - {size_info['price_3']} руб\n"
                              f"4 шт - {size_info['price_4']} руб\n"
                              f"5 шт - {size_info['price_5']} руб\n"
                              f"6 шт - {size_info['price_6']} руб\n\n"
                              f"Что будем менять?",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='Название',
                                          callback_data=edit_size_data.new(size_id=size_id,
                                                                           subject='name')
                                      )
                                  ],
                                  [
                                      InlineKeyboardButton(
                                          text='Цены',
                                          callback_data=edit_size_data.new(size_id=size_id,
                                                                           subject='price')
                                      )
                                  ],
                                  [
                                      back_button
                                  ]
                              ]))
    await AddAdmin.EditItemEditSizeById.set()


@dp.callback_query_handler(text='back', state=[AddAdmin.EditItemNewSizeName,
                                               AddAdmin.EditItemNewSizePrices,
                                               AddAdmin.EditItemRemoveSizes,
                                               AddAdmin.EditItemEditSizes,
                                               AddAdmin.EditItemEditSizeById])
async def back_to_sizes(call: CallbackQuery, state: FSMContext):
    """Назад к выбору действия с размерами"""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item_id = data.get('product_id')
    item_has_sizes = await db.product_has_size(item_id)
    if item_has_sizes:
        sizes = await db.get_product_sizes(item_id)
        list_of_sizes = await get_sizes(sizes)
        await call.message.answer('У товара есть размеры:\n'
                                  f'{list_of_sizes}\n\n'
                                  f'Выберите действие:',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text="Добавить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='add_size')
                                          )
                                      ],
                                      [
                                          InlineKeyboardButton(
                                              text="Удалить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='remove_size')
                                          )
                                      ],
                                      [
                                          InlineKeyboardButton(
                                              text="Изменить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='edit_size')
                                          )
                                      ],
                                      [
                                          back_button
                                      ]
                                  ]))
    else:
        await call.message.answer('У товара нет размеров.\n'
                                  'Выберите действие:',
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text="Добавить размер",
                                              callback_data=edit_item_sizes_data.new(item_id=item_id,
                                                                                     subject='add_size')
                                          )
                                      ],
                                      [
                                          back_button
                                      ]
                                  ]))
    await AddAdmin.EditItemBySizes.set()


@dp.callback_query_handler(text='back', state=[AddAdmin.EditItemByName,
                                               AddAdmin.EditItemByDescription,
                                               AddAdmin.EditItemByPhoto,
                                               AddAdmin.EditItemByPrices,
                                               AddAdmin.EditItemByAvailability,
                                               AddAdmin.EditItemBySizes])
async def back_to_edit(call: CallbackQuery, state: FSMContext):
    """Назад к изменению товара"""
    await call.message.edit_reply_markup()
    await call.answer('Назад')
    data = await state.get_data()
    product_id = data.get('product_id')
    await state.update_data(product_id=product_id)
    product_info = await db.get_product_info(product_id)
    await call.message.answer('Вы выбрали:')
    await bot.send_photo(call.from_user.id, photo=product_info['product_photo_id'],
                         caption=f"Название: {product_info['product_name']}\n"
                                 f"Описание: {product_info['product_description']}\n"
                                 f"Цены:\n"
                                 f"1 шт - {product_info['price_1']} руб\n"
                                 f"2 шт - {product_info['price_2']} руб\n"
                                 f"3 шт - {product_info['price_3']} руб\n"
                                 f"4 шт - {product_info['price_4']} руб\n"
                                 f"5 шт - {product_info['price_5']} руб\n"
                                 f"6 шт - {product_info['price_6']} руб\n"
                                 f"Товар в продаже - {product_info['is_product_available']}\n\n"
                                 f"Что будем менять?",
                         reply_markup=await get_edit_item_markup(product_info))
    await AddAdmin.EditItemByWaitSubject.set()


@dp.callback_query_handler(text='back', state=[AddAdmin.TakeOrders,
                                               AddAdmin.ConfirmDeliveryOrders])
@dp.callback_query_handler(text='cancel', state=[AddAdmin.EditItemByWaitSubject,
                                                 AddAdmin.EditItemById,
                                                 AddAdmin.EditItem,
                                                 AddAdmin.EditMetroName,
                                                 AddAdmin.EditMetro,
                                                 AddAdmin.WaitName,
                                                 AddAdmin.ItemConfirm,
                                                 AddAdmin.ItemSize,
                                                 AddAdmin.ItemPrice,
                                                 AddAdmin.ItemPhoto,
                                                 AddAdmin.ItemDescription,
                                                 AddAdmin.ItemName,
                                                 AddAdmin.WaitId,
                                                 AddAdmin.WaitDeleteAdmins,
                                                 AddAdmin.WaitMetroName,
                                                 AddAdmin.WaitDeleteMetro,
                                                 AddAdmin.NewLocationMetro,
                                                 AddAdmin.NewLocationName,
                                                 AddAdmin.NewLocationAddress,
                                                 AddAdmin.SaveNewLocation,
                                                 AddAdmin.LocalObjectMetro,
                                                 AddAdmin.LocalObjectLocation,
                                                 AddAdmin.LocalObjectName,
                                                 AddAdmin.DeleteLocation,
                                                 AddAdmin.RemoveLocalObject,
                                                 AddAdmin.NewCategory,
                                                 AddAdmin.RemoveCategory,
                                                 AddAdmin.ItemCategory,
                                                 AddAdmin.ItemSizeName,
                                                 AddAdmin.ItemSizePrice,
                                                 AddAdmin.RemoveItemCategory,
                                                 AddAdmin.RemoveItem,
                                                 AddAdmin.AdminSellerName,
                                                 AddAdmin.AdminSellerID,
                                                 AddAdmin.AdminSellerMetro,
                                                 AddAdmin.AdminSellerLocation,
                                                 AddAdmin.RemoveSellerAdmin,
                                                 AddAdmin.SellerName,
                                                 AddAdmin.SellerID,
                                                 AddAdmin.SellerMetro,
                                                 AddAdmin.RemoveSeller,
                                                 AddAdmin.CourierName,
                                                 AddAdmin.CourierID,
                                                 AddAdmin.CourierMetro,
                                                 AddAdmin.CourierLocation,
                                                 AddAdmin.RemoveCourier,
                                                 AddAdmin.ResetSellerAdmin,
                                                 AddAdmin.ResetSeller,
                                                 AddAdmin.ResetCourier,
                                                 AddAdmin.RemoveCategoryFromStocks,
                                                 AddAdmin.ReturnCategoryToStocks,
                                                 AddAdmin.RemoveItemFromStockCategory,
                                                 AddAdmin.RemoveItemFromStockProduct,
                                                 AddAdmin.ReturnItemToStockCategory,
                                                 AddAdmin.ReturnItemToStockProduct,
                                                 AddAdmin.ChangeSellerAdmin,
                                                 AddAdmin.ChangeSellerAdminMetro,
                                                 AddAdmin.ChangeSellerAdminLocation,
                                                 AddAdmin.ChangeSeller,
                                                 AddAdmin.ChangeSellerMetro,
                                                 AddAdmin.ChangeSellerLocation,
                                                 AddAdmin.ChangeCourier,
                                                 AddAdmin.ChangeCourierMetro,
                                                 AddAdmin.ChangeCourierLocation,
                                                 AddAdmin.SetAbout,
                                                 AddAdmin.PromoPhoto,
                                                 AddAdmin.PromoCaption,
                                                 AddAdmin.PromoConfirm,
                                                 AddAdmin.BanReason,
                                                 AddAdmin.BanID,
                                                 AddAdmin.UnBanID,
                                                 AddAdmin.SellerLocation,
                                                 AddAdmin.DeliveryCategoryName,
                                                 AddAdmin.DeliveryItemCategory,
                                                 AddAdmin.DeliveryItemName,
                                                 AddAdmin.DeliveryItemPrice,
                                                 AddAdmin.RemoveDeliveryCategory,
                                                 AddAdmin.RemoveDeliveryItemCat,
                                                 AddAdmin.RemoveDeliveryItem,
                                                 AddAdmin.RemoveDeliveryItemFromStockCategory,
                                                 AddAdmin.RemoveDeliveryItemFromStockProduct,
                                                 AddAdmin.ReturnDeliveryItemToStockCategory,
                                                 AddAdmin.ReturnDeliveryItemToStockProduct,
                                                 AddAdmin.EditDeliveryItem,
                                                 AddAdmin.EditDeliveryItemID,
                                                 AddAdmin.EditDeliveryItemPrice])
async def cancel_add_admin(call: CallbackQuery, state: FSMContext):
    """Кнопка отмены"""
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Вы отменили/завершили операцию')
