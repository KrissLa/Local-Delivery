import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from filters.users_filters import IsAdminMessage
from keyboards.default.menu import menu_keyboard
from keyboards.inline.callback_datas import bonuses_data
from keyboards.inline.inline_keyboards import generate_keyboard_with_categories, generate_keyboard_with_none_categories, \
    generate_keyboard_with_metro, cart_markup, cancel_order_by_use_button
from loader import db, dp
from states.menu_states import Menu, SignUpUser
from utils.check_states import states_for_menu, reset_state
from utils.emoji import warning_em, error_em, attention_em
from utils.product_list import get_product_list
from utils.send_messages import send_cart
from utils.temp_orders_list import get_objects_list_message, get_temp_orders_list_message, get_final_price


@dp.message_handler(commands=['menu'], state=['*'])
async def menu(message: types.Message, state: FSMContext):
    """Отправляем меню"""
    if await state.get_state() == ['Menu:WaitReasonUser', 'SelectCourier:WaitReasonCourier',
                                   'SelectCourier:WaitReason', 'SelectCourier:WaitReasonActive']:
        await message.answer('Напишите причину отмены..',
                             reply_markup=menu_keyboard)
    else:
        await message.answer('Отправляю меню',
                             reply_markup=menu_keyboard)


@dp.message_handler(commands=['cart'], state='*')
async def cart(message: types.Message, state: FSMContext):
    """Корзина"""
    await reset_state(state, message)
    temp_orders = await db.get_temp_orders(message.from_user.id)
    if temp_orders:
        list_products = await get_temp_orders_list_message(temp_orders)
        final_price = await get_final_price(temp_orders)
        await state.update_data(list_products=list_products)
        await state.update_data(final_price=final_price)
        await send_cart(temp_orders, message.from_user.id)
        await message.answer(f'Сумма заказа - {final_price} руб.\n'
                             'Оформить заказ\n'
                             f'{attention_em} Доставка работает в будни с 11 до 17',
                             reply_markup=cart_markup)
        await Menu.OneMoreOrNext.set()
    else:
        await message.answer('Ваша корзина пуста')


@dp.message_handler(commands=['clear_cart'], state=['*'])
async def cart(message: types.Message, state: FSMContext):
    """Корзина"""
    await reset_state(state, message)
    await db.clear_cart(message.from_user.id)
    await db.clear_empty_orders(message.from_user.id)
    await message.answer('Корзина очищена.\n'
                         'Вы в главном меню',
                         reply_markup=menu_keyboard)

@dp.message_handler(commands=['order_status'], state=['*'])
async def get_order_status(message: types.Message, state: FSMContext):
    """Статус заказа"""
    await reset_state(state, message)
    orders = await db.get_orders_for_user(message.from_user.id)
    if orders:
        for order in orders:
            if order['order_delivery_method'] == 'Доставка':
                if order['order_time_for_delivery']:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{await get_product_list(order['order_id'])}\n"
                                         f"Стоимость: {order['order_final_price']} руб.\n"
                                         f"Будет доставлен в {order['order_time_for_delivery'].strftime('%H:%M')}\n"
                                         f"Статус заказа - {order['order_status']}\n\n",
                                         reply_markup=await cancel_order_by_use_button(order['order_id']))
                else:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{await get_product_list(order['order_id'])}\n"
                                         f"Стоимость: {order['order_final_price']} руб.\n"
                                         f"Статус заказа - {order['order_status']}\n\n",
                                         reply_markup=await cancel_order_by_use_button(order['order_id']))
            else:
                if order['order_time_for_delivery']:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{await get_product_list(order['order_id'])}\n"
                                         f"Стоимость: {order['order_final_price']} руб.\n"
                                         f"Будет готов в {order['order_time_for_delivery'].strftime('%H:%M')}\n"
                                         f"Статус заказа - {order['order_status']}\n\n",
                                         reply_markup=await cancel_order_by_use_button(order['order_id']))
                else:
                    await message.answer(f"Заказ № {order['order_id']}\n"
                                         f"{await get_product_list(order['order_id'])}"
                                         f"Стоимость: {order['order_final_price']} руб.\n"
                                         f"Статус заказа - {order['order_status']}\n\n",
                                         reply_markup=await cancel_order_by_use_button(order['order_id']))
        await Menu.OrderStatus.set()
    else:
        await message.answer('Нет активных заказов')


@dp.message_handler(IsAdminMessage(), commands=['first_start'], state=['*'])
async def first_start(message: types.Message, state: FSMContext):
    """Первый запуск"""
    await state.finish()
    text = [
        'Список команд: ',
        '1. Нажать при первом запуске, перед добавлением станций метро, локаций, и объектов доставки'
        ' чтобы бот не ругался на то, что Вы не закреплены за локацией - /first_start\n',
        'Общие команды:',
        '2. Получить справку - /help',
        '3. Корзина - /cart',
        '4. Показать меню - /menu',
        '5. Показать статус заказа - /order_status\n',
        'Команды админа:',
        '6. Создать промо пост - /publish_post',
        '7. Добавить/изменить описание компании - /set_about\n',
        'Работа с персоналом:',
        '   Добавление:',
        '8. Добавть админа - /add_admin',
        '9. Добавить админа локации - /add_seller_admin',
        '10. Добавить продавца - /add_seller',
        '11. Добавить курьера - /add_courier',
        '   Удаление:',
        '12. Удалить админа - /delete_admin',
        '13. Удалить админа локации - /remove_seller_admin',
        '14. Удалить продавца - /remove_seller',
        '15. Удалить курьера - /remove_courier',
        '   Локации персонала:',
        '16. Открепить админа локации от локации - /reset_seller_admin_location',
        '17. Открепить продавца от локации - /reset_seller_location',
        '18. Открепить курьера от локации - /reset_courier_location',
        '19. Привязать админа локации к другой локации - /change_seller_admin_location',
        '20. Привязать продавца к другой локации - /change_seller_location',
        '21. Привязать курьера к другой локации - /change_courier_location\n',
        'Работа с локациями:',
        '22. Добавить станцию метро - /add_metro',
        '23. Добавить точку продаж - /add_newlocation',
        '24. Добавить объект локальной доставки - /add_local_object',
        '25. Удалить станцию метро - /delete_metro',
        '26. Удалить точку продаж - /delete_location',
        '27. Удалить объект локальной доставки - /remove_local_object',
        '28. Редактировать метро - /edit_metro\n',
        'Работа с категориями:',
        '29. Добавить категорию товара - /add_category',
        '30. Удалить категорию товара - /remove_category',
        '31. Убрать категорию из меню - /remove_category_from_stock',
        '32. Вернуть категорию в меню - /return_category_to_stock\n',
        'Работа с товарами:',
        '33. Добавить товар - /add_item',
        '34. Удалить товар - /remove_item',
        '35. Убрать товар из меню - /remove_item_from_stock',
        '36. Вернуть товар в меню - /return_item_to_stock',
        '37. Редактировать товар - /edit_item\n',
        'Работа с пользователями:',
        '38. Заблокировать пользователя - /ban_user',
        '39. Разблокировать пользователя - /unban_user',
    ]
    await message.answer('\n'.join(text))


@dp.message_handler(text="О сервисе", state=states_for_menu)
@dp.message_handler(text="О сервисе", state='*')
async def show_about(message: types.Message, state: FSMContext):
    """Отправляем инфу о компании"""
    await reset_state(state, message)
    about = await db.get_about()
    list_of_object = await db.get_objects()
    objects = await get_objects_list_message(list_of_object)
    await message.answer(f'{about}\n\n'
                         f'Адреса где работает доставка:\n\n'
                         f'{objects}')


@dp.message_handler(text="Меню", state=states_for_menu)
@dp.message_handler(text='Меню', state='*')
async def send_categories_menu(message: types.Message, state: FSMContext):
    """Отправляем категории товаров, доступные в локации пользователя"""
    await reset_state(state, message)
    categories = await db.get_categories_for_user_location_id(message.from_user.id)
    if categories:
        await message.answer('Выберите категорию меню',
                             reply_markup=await generate_keyboard_with_categories(categories))
    else:
        await message.answer('Нет доступных категорий.',
                             reply_markup=await generate_keyboard_with_none_categories())
    await Menu.WaitCategory.set()


@dp.message_handler(text="Профиль", state=states_for_menu)
@dp.message_handler(text="Профиль", state='*')
async def send_categories_menu(message: types.Message, state: FSMContext):
    """Отправляем информацию профиля"""
    await reset_state(state, message)
    try:
        user_info = await db.get_user_profile_info(message.from_user.id)
        if user_info['user_address']:
            await message.answer(f"Ваш профиль\n"
                                 f"\n"
                                 f"User ID: {user_info['user_telegram_id']}\n"
                                 f"Адрес доставки: {user_info['local_object_name']}\n"
                                 f"Параметры доставки: {user_info['user_address']}",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='Изменить',
                                             callback_data='change_profile'
                                         )
                                     ]
                                 ]))
        else:
            await message.answer(text=f"Ваш профиль\n"
                                      f"\n"
                                      f"User ID: {user_info['user_telegram_id']}\n"
                                      f"Адрес доставки: {user_info['local_object_name']}\n"
                                      f"{warning_em} Параметры доставки: Не указаны",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='Изменить',
                                             callback_data='change_profile'
                                         )
                                     ]
                                 ]))
    except Exception as err:
        logging.error(err)
        await message.answer(f"{error_em} Сначала нужно выбрать ближайшую станцию метро и точку продаж",
                             reply_markup=await generate_keyboard_with_metro())
        await SignUpUser.Metro.set()


@dp.message_handler(text="Акции и бонусы", state=states_for_menu)
@dp.message_handler(text="Акции и бонусы", state='*')
async def send_categories_menu(message: types.Message, state: FSMContext):
    """Нажатие на кнопку акции и бонусы"""
    await reset_state(state, message)
    data = await db.get_bonus_and_location_address(message.from_user.id)
    bot_user = await dp.bot.get_me()
    if data['bonus'] == 0:
        await message.answer("Ваш бонусный баланс:\n"
                             f"Любой гриль ролл из ассортимента - {data['bonus']} шт.\n")
    else:
        await message.answer("Ваш бонусный баланс:\n"
                             f"Любой гриль ролл из ассортимента - {data['bonus']} шт.\n"
                             f"Подойдите к продавцу и нажмите Получить\n"
                             f"Ближайший адрес: {data['location_address']}",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Получить',
                                         callback_data=bonuses_data.new(count_bonus=data['bonus'])
                                     )
                                 ]
                             ]))

    await message.answer(f'Пригласите друга и после первого заказа мы подарим Вам 1 ролл на Ваш выбор.\n'
                         f'\n'
                         f'Мы также будем дарить Вам по 1 роллу с каждого 10 заказа любого из Ваших друзей.\n\n'
                         f'{attention_em} Промо акция действует бессрочно и только при заказе через данный сервисный бот.\n\n'
                         f'Ваша реферальная ссылка:\n'
                         f'http://t.me/{bot_user.username}?start={message.from_user.id}',
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='Показать в QR code',
                                         callback_data='show_qr_ref_link'
                                     ),
                                     InlineKeyboardButton(
                                         text='Поделиться',
                                         switch_inline_query='share'
                                     )
                                 ]
                             ]
                         ))
