from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callback_datas import bonuses_data
from keyboards.inline.inline_keyboards import generate_keyboard_with_categories, generate_keyboard_with_none_categories, \
    generate_keyboard_with_metro
from loader import db, dp
from states.menu_states import Menu, SignUpUser
from utils.check_states import states_for_menu, reset_state
from utils.temp_orders_list import get_objects_list_message


@dp.message_handler(text="О сервисе", state=states_for_menu)
@dp.message_handler(text="О сервисе")
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
@dp.message_handler(text='Меню')
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
@dp.message_handler(text="Профиль")
async def send_categories_menu(message: types.Message, state: FSMContext):
    """Отправляем информацию профиля"""
    await reset_state(state, message)
    try:
        user_info = await db.get_user_profile_info(message.from_user.id)
        print(user_info)
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
                                      f"Параметры доставки: Не указаны",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='Изменить',
                                             callback_data='change_profile'
                                         )
                                     ]
                                 ]))
    except Exception as err:
        await message.answer(f"Сначала нужно выбрать ближайшую станцию метро и точку продаж",
                             reply_markup=await generate_keyboard_with_metro())
        await SignUpUser.Metro.set()


@dp.message_handler(text="Акции и бонусы", state=states_for_menu)
@dp.message_handler(text="Акции и бонусы")
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
                         f'! Промо акция действует бессрочно и только при заказе через данный сервисный бот.\n\n'
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
