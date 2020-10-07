import logging
from re import compile

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery

from filters.users_filters import HasNoMetro, HasNoLocation, HasNoLocalObject, IsNotClientMessage
from keyboards.default.menu import menu_keyboard
from keyboards.inline.callback_datas import metro_data, local_object_data
from keyboards.inline.inline_keyboards import generate_keyboard_with_metro, get_available_local_objects
from loader import dp, db
from states.menu_states import SignUpUser
from utils.check_states import reset_state
from utils.emoji import attention_em


@dp.message_handler(CommandStart(deep_link=compile(r'\d\w*')), state=['*'])
async def bot_start_referal(message: types.Message, state: FSMContext):
    """Отлавливаем реферальные ссылки"""
    await reset_state(state, message)
    user_id = message.from_user.id
    if await db.get_user(user_id):
        await message.answer('Вы уже зарегистрированы в боте. Пожалуйста, воспользуйтесь командами из меню.',
                             reply_markup=menu_keyboard)
    else:
        try:
            deep_link_args = int(message.get_args())
            if await db.get_user(deep_link_args):
                await state.update_data(inviter_id=deep_link_args)
                await message.answer(f"Приветствуем! \n"
                                     f"Ваш реферальный код принят!"
                                     f"\nДля оформления заказа выберите ближайшую станцию метро.",
                                     reply_markup=await generate_keyboard_with_metro())
                await SignUpUser.Metro.set()
            else:
                await message.answer(f"Приветствуем! \n"
                                     f"Ваша реферальная ссылка недействительна."
                                     f"\nДля оформления заказа выберите ближайшую станцию метро.",
                                     reply_markup=await generate_keyboard_with_metro())
                await SignUpUser.Metro.set()
        except Exception as err:
            logging.error(err)
            await message.answer(f"Приветствуем! \n"
                                 f"Ваша реферальная ссылка недействительна."
                                 f"\nДля оформления заказа выберите ближайшую станцию метро.",
                                 reply_markup=await generate_keyboard_with_metro())
            await SignUpUser.Metro.set()


@dp.message_handler(HasNoMetro(), IsNotClientMessage(), state=['*'])
@dp.message_handler(HasNoLocation(), IsNotClientMessage(), state=['*'])
@dp.message_handler(HasNoLocalObject(), IsNotClientMessage(), state=['*'])
@dp.message_handler(CommandStart(deep_link=None), state=['*'])
async def bot_start(message: types.Message, state: FSMContext):
    """Нажатие на старт без реферального кода"""
    await reset_state(state, message)
    user_id = message.from_user.id
    if await db.get_user(user_id):
        await message.answer('Вы уже зарегистрированы в боте. Пожалуйста, воспользуйтесь командами из меню.',
                             reply_markup=menu_keyboard)
    else:
        await message.answer(f"Приветствуем! \nДля оформления заказа выберите ближайшую станцию метро.",
                             reply_markup=await generate_keyboard_with_metro())
        await SignUpUser.Metro.set()


@dp.callback_query_handler(metro_data.filter(), state=SignUpUser.Metro)
async def get_user_location(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Предлагаем пользователю выбрать локацию"""
    await call.answer(cache_time=10)
    await call.message.edit_reply_markup()
    metro_id = int(callback_data.get('metro_id'))
    await state.update_data(metro_id=metro_id)
    metro_name = await db.get_metro_name_by_metro_id(metro_id)
    await call.message.answer(f"Вы выбрали {metro_name}. \n"
                              f"Выберите объект локальной доставки",
                              reply_markup=await get_available_local_objects(metro_id))
    await SignUpUser.Location.set()


@dp.callback_query_handler(text='back', state=SignUpUser.Location)
async def none_location_list(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer(f"Приветствуем! \nДля оформления заказа выберите ближайшую станцию метро.",
                              reply_markup=await generate_keyboard_with_metro())
    await SignUpUser.Metro.set()


@dp.callback_query_handler(local_object_data.filter(), state=SignUpUser.Location)
async def set_user_location(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Сохраняем данные в бд. Отправляем меню"""
    await call.answer(text='Локация выбрана', cache_time=10)
    data = await state.get_data()
    inviter_id = data.get('inviter_id')
    await call.message.edit_reply_markup()
    local_object_id = int(callback_data.get('local_object_id'))
    loc_data = await db.get_local_object_data_by_id(local_object_id)
    bot_user = await dp.bot.get_me()
    if inviter_id:
        await db.add_user_with_inviter(user_telegram_id=call.from_user.id,
                                       user_metro_id=loc_data['local_object_metro_id'],
                                       user_location_id=loc_data['local_object_location_id'],
                                       user_local_object_id=local_object_id,
                                       inviter_id=inviter_id
                                       )
        await db.add_referral(inviter_id)
    else:
        await db.add_user(user_telegram_id=call.from_user.id,
                          user_metro_id=loc_data['local_object_metro_id'],
                          user_location_id=loc_data['local_object_location_id'],
                          user_local_object_id=local_object_id
                          )
    await state.finish()
    await call.message.answer(f'Все готово!\n'
                              f'Мы сохранили Ваш выбор {loc_data["local_object_name"]}.\n'
                              f'Теперь Вы можете заказывать еду и напитки из нашего меню с доставкой к Вам на работу.\n'
                              f'{attention_em} Вы всегда можете изменить эти настройки в Вашем профиле.\n'
                              f'Ваша ссылка для приглашения друзей:\n'
                              f'http://t.me/{bot_user.username}?start={call.from_user.id}\n'
                              f'{attention_em} Подробнее о реферальной системе можно узнать в разделе "Акции и бонусы".',
                              reply_markup=menu_keyboard)
