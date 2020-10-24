from datetime import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytz import timezone

from keyboards.inline.callback_datas import bonuses_data, cancel_bonus_order_data
from keyboards.inline.inline_keyboards import back_cancel_bonus_markup
from loader import dp, db, bot
from states.bonus_state import Bonus
from utils.emoji import attention_em, error_em, success_em
from utils.send_messages import send_message_to_sellers_bonus


@dp.callback_query_handler(text='cancel_bonus_order', state=Bonus.Count)
@dp.callback_query_handler(text='back', state=Bonus.Count)
async def back_to_bonus(call: CallbackQuery, state: FSMContext):
    """Назад к бонусу"""
    await call.answer('Назад')
    await call.message.edit_reply_markup()
    data = await db.get_bonus_and_location_address(call.from_user.id)
    bot_user = await dp.bot.get_me()
    if data['bonus'] == 0:
        await call.message.answer("Ваш бонусный баланс:\n"
                                  f"Любой гриль ролл из ассортимента - {data['bonus']} шт.\n")
    else:
        await call.message.answer("Ваш бонусный баланс:\n"
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

    await call.message.answer(f'Пригласите друга и после первого заказа мы подарим Вам 1 ролл на Ваш выбор.\n'
                              f'\n'
                              f'Мы также будем дарить Вам по 1 роллу с каждого 10 заказа любого из Ваших друзей.\n\n'
                              f'{attention_em} Промо акция действует бессрочно и только при заказе через данный сервисный бот.\n\n'
                              f'Ваша реферальная ссылка:\n'
                              f'http://t.me/{bot_user.username}?start={call.from_user.id}',
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
    await state.finish()


@dp.callback_query_handler(text='show_qr_ref_link')
async def show_qr_ref_code(call: CallbackQuery):
    """Генерируем qr code"""
    bot_user = await dp.bot.get_me()

    await bot.send_photo(chat_id=call.from_user.id,
                         photo=f"http://qrcoder.ru/code/?http%3A%2F%2Ft.me%2F{bot_user.username}%3Fstart%3D{call.from_user.id}&4&0")


@dp.callback_query_handler(bonuses_data.filter())
async def get_bonus_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Просим написать количество"""
    count_bonus = int(callback_data.get('count_bonus'))
    await state.update_data(count_bonus=count_bonus)
    await call.message.answer('Напишите количество.\n'
                              f'Вам доступно - {count_bonus} шт.',
                              reply_markup=back_cancel_bonus_markup)
    await Bonus.Count.set()


@dp.message_handler(state=Bonus.Count)
async def get_count_bonus(message: types.Message, state: FSMContext):
    """Получаем количество"""
    data = await state.get_data()
    count_bonus = data.get('count_bonus')
    try:
        quantity = int(message.text)
        if quantity > count_bonus:
            await message.answer(f'{error_em} Напишите количество.\n'
                                 f"Вам доступно - {count_bonus} шт.",
                                 reply_markup=back_cancel_bonus_markup)
            await Bonus.Count.set()
        elif quantity == 0:
            await message.answer(f'{error_em} Введите что-то кроме 0.\n'
                                 f"Вам доступно - {count_bonus} шт.",
                                 reply_markup=back_cancel_bonus_markup)
            await Bonus.Count.set()
        else:
            bonus_location_id = await db.get_user_location_id(message.from_user.id)
            await db.add_bonus_order(bonus_location_id,
                                     datetime.now(timezone("Europe/Moscow")),
                                     await db.get_user_id(message.from_user.id),
                                     datetime.now(timezone("Europe/Moscow")),
                                     quantity,
                                     'Ожидание продавца')
            await db.change_bonus_minus(user_id=message.from_user.id,
                                        count_bonus=quantity)
            bonus_order_info = await db.get_bonus_order_info(message.from_user.id)
            sellers_list = await db.get_sellers_id_for_location(bonus_order_info['bonus_order_location_id'])
            if sellers_list:
                await message.answer(f'Ваш заказ № {bonus_order_info["bonus_order_id"]}Б сформирован - '
                                     f'{bonus_order_info["bonus_order_quantity"]} шт.\n'
                                     f'{attention_em} Пожалуйста, покажите это сообщение продавцу',
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [
                                             InlineKeyboardButton(
                                                 text='Отменить заказ',
                                                 callback_data=cancel_bonus_order_data.new(
                                                     b_order_id=bonus_order_info["bonus_order_id"],
                                                     quantity=quantity))
                                         ]
                                     ]))
                await send_message_to_sellers_bonus(sellers_list, bonus_order_info)
                await state.finish()
            else:
                await message.answer('Нет доступных продавцов. Попробуйте позже.')
                await db.change_bonus_plus(user_id=message.from_user.id,
                                           count_bonus=quantity)
                await db.set_bonus_order_status(bonus_order_info["bonus_order_id"],
                                                "Отклонен",
                                                'Не нашел доступных продавцов')
                await state.finish()

    except Exception as err:
        logging.error(err)
        await message.answer('Напишите количество.\n'
                             f"Вам доступно - {count_bonus} шт.",
                             reply_markup=back_cancel_bonus_markup)
        await Bonus.Count.set()


@dp.callback_query_handler(cancel_bonus_order_data.filter())
async def cancel_bonus_order(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """Отмена бонусного заказа после ввода количества"""
    await call.message.edit_reply_markup()
    b_order_id = int(callback_data.get('b_order_id'))
    quantity = int(callback_data.get('quantity'))
    bonus_status = await db.get_bonus_order_status(b_order_id)
    if bonus_status == 'Ожидание продавца':
        await db.change_bonus_plus(user_id=call.from_user.id,
                                   count_bonus=quantity)
        await db.set_bonus_order_status(b_order_id,
                                        "Отменен пользователем до принятия продавцом",
                                        'Причина не указана')
        await db.set_bonus_order_canceled_at(b_order_id)
        await state.finish()
        await call.message.answer(f'{success_em}Ваш заказ № {b_order_id}Б отменен.')
    else:
        await call.message.answer(f'{error_em} Ваш заказ уже подтвержден. Чтобы отменить его, пожалуйста, подойдите к '
                                  f'продавцу.')


@dp.callback_query_handler(text='return_to_bot', state=Bonus.WaitSeller)
async def return_to_bot(call: CallbackQuery, state: FSMContext):
    """Вернуться к боту"""
    await call.message.edit_reply_markup()
    await call.message.answer("Вы в главном меню")
    await state.finish()
