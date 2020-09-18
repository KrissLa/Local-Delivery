from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import IsAdminMessage
from keyboards.default.menu import menu_keyboard
from loader import dp, db


@dp.message_handler(IsAdminMessage(), commands=['first_start'], state=['*'])
async def first_start(message: types.Message, state: FSMContext):
    """Первый запуск"""
    await state.finish()
    text = [
        'Список команд: ',
        '/first_start - Нажать при первом запуске, перед добавлением станций метро, локаций, и объектов доставки'
        ' чтобы бот не ругался на то, что Вы не закреплены за локацией',
        '/start - Начать диалог',
        '/help - Получить справку',
        '/cart - Корзина',  # НЕ ГОТОВО
        '/clear_cart - Очистить корзину',  # НЕ ГОТОВО
        '/menu - Показать меню',  # НЕ ГОТОВО
        '/order_status - Показать статус заказа',  # НЕ ГОТОВО
        '/publish_post - Создать промо пост',  # НЕ ГОТОВО
        '/set_about - Добавить/изменить описание компании',  # НЕ ГОТОВО
        '/add_admin - Добавть админа',
        '/delete_admin - Удалить админа',
        '/add_metro - Добавить станцию метро',
        '/delete_metro - Удалить станцию метро',
        '/add_newlocation - Добавить точку продаж',
        '/delete_location - Удалить точку продаж',
        '/add_local_object - Добавить объект локальной доставки',
        '/remove_local_object - Удалить объект локальной доставки',
        '/add_category - Добавить категорию товара',
        '/remove_category - Удалить категорию товара',
        '/add_item - Добавить товар',
        '/remove_item - Удалить товар',
        '/add_seller_admin - Добавить админа локации',
        '/remove_seller_admin - Удалить админа локации',
        '/add_seller - Добавить продавца',
        '/remove_seller - Удалить продавца',
        '/add_courier - Добавить курьера',
        '/remove_courier - Удалить курьера',
        '/reset_seller_admin_location - Открепить админа локации от локации',
        '/reset_seller_location - Открепить продавца от локации',
        '/reset_courier_location - Открепить курьера от локации',
        '/remove_category_from_stock - Убрать категорию из меню',
        '/return_category_to_stock - Вернуть категорию в меню',
        '/remove_item_from_stock - Убрать товар из меню',
        '/return_item_to_stock - Вернуть товар в меню',
        '/change_seller_admin_location - Привязать админа локации к другой локации',
        '/change_seller_location - Привязать продавца к другой локации',
        '/change_courier_location - Привязать курьера к другой локации',
        '/edit_metro - Редактировать метро',
        '/edit_item - Редактировать товар',
    ]
    await message.answer('\n'.join(text))



@dp.callback_query_handler(text='cancel_order', state=['*'])
async def cancel_order(call: CallbackQuery, state: FSMContext):
    """Отмена заказа, очистка корзины"""
    await call.message.edit_reply_markup()
    await state.finish()
    await db.clear_cart(call.from_user.id)
    await db.clear_empty_orders(call.from_user.id)
    await call.answer("Вы отменили заказ. Корзина товаров очищена")
    await call.message.answer('Вы в главном меню',
                              reply_markup=menu_keyboard)
