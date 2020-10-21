from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from filters.users_filters import HasNoLocation, IsClientMessage, HasNoLocalObject, HasNoMetro, IsNotClientMessage
from keyboards.inline.inline_keyboards import generate_keyboard_with_metro_profile
from loader import dp, db
from states.profile_states import ProfileState
from utils.check_states import reset_state
from utils.emoji import warning_em


@dp.message_handler(IsNotClientMessage(), state=ProfileState.WaitAddress)
async def set_change_profile(message: types.Message, state: FSMContext):
    """Обновляем данные пользователя в бд"""
    data = await state.get_data()
    local_object_id = data.get('local_object_id')
    loc_data = await db.get_local_object_data_by_id(local_object_id)
    await db.add_user_with_address(message.from_user.id,
                              loc_data['local_object_metro_id'],
                              loc_data['local_object_location_id'],
                              local_object_id,
                              message.text
                              )
    await message.answer("Данные профиля обновлены.\n"
                         f"User ID: {message.from_user.id}\n"
                         f"Адрес доставки: {loc_data['local_object_name']}\n"
                         f"Параметры доставки: {message.text}\n",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [
                                 InlineKeyboardButton(
                                     text='Изменить',
                                     callback_data='change_profile'
                                 )
                             ]
                         ]
                         ))
    await state.finish()



@dp.message_handler(HasNoMetro(), IsClientMessage(), state=['*'])
@dp.message_handler(HasNoLocation(), IsClientMessage(), state=['*'])
@dp.message_handler(HasNoLocalObject(), IsClientMessage(), state=['*'])
async def bot_echo(message: types.Message, state: FSMContext):
    await reset_state(state, message)
    await message.answer(f"{warning_em} Сначала Вам нужно выбрать точку продаж. Вы всегда сможете "
                         f"изменить ее в своем профиле\n"
                         f"Для начала выберите ближайшую станцию метро.",
                         reply_markup=await generate_keyboard_with_metro_profile())
    await ProfileState.WaitMetro.set()


@dp.callback_query_handler(HasNoLocalObject(), IsClientMessage(),
                           text='cancel', state=[ProfileState.WaitMetro,
                                                 ProfileState.WaitLocation,
                                                 ProfileState.WaitAddress])
@dp.callback_query_handler(HasNoLocation(), IsClientMessage(),
                           text='cancel', state=[ProfileState.WaitMetro,
                                                 ProfileState.WaitLocation,
                                                 ProfileState.WaitAddress])
async def cancel(call: CallbackQuery, state: FSMContext):
    """Отмена"""
    await state.finish()
    await call.message.answer(f'{warning_em} Вы отменили операцию, но для продолжения нужно будет выбрать локацию.')



