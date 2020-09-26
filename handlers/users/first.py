from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import HasNoLocation, IsClientMessage, HasNoLocalObject, HasNoMetro
from keyboards.inline.inline_keyboards import generate_keyboard_with_metro_profile
from loader import dp
from states.profile_states import ProfileState


@dp.message_handler(HasNoMetro(), IsClientMessage(), state=['*'])
@dp.message_handler(HasNoLocation(), IsClientMessage(), state=['*'])
@dp.message_handler(HasNoLocalObject(), IsClientMessage(), state=['*'])
async def bot_echo(message: types.Message):
    await message.answer(f"Сначала Вам нужно выбрать точку продаж. Вы всегда сможете "
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
    await call.message.answer('Вы отменили операцию, но для продолжения нужно будет выбрать локацию.')



