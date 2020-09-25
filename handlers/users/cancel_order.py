from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.users_filters import IsAdminMessage, IsBanned
from keyboards.default.menu import menu_keyboard
from loader import dp, db
from utils.misc import rate_limit


@rate_limit(25, 'help')
@dp.message_handler(IsBanned(), state=['*'])
async def ban(message: types.Message):
    """Ответ забаненым"""
    reason = await db.get_reason_for_ban(message.from_user.id)
    await message.answer(f'Вы забанены\n'
                         f'Причина: {reason}')


@dp.message_handler(IsAdminMessage(), commands=['first_start'], state=['*'])
async def first_start(message: types.Message, state: FSMContext):
    """Первый запуск"""
    await state.finish()
    text = [
        'Список команд: ',
        '1. /first_start - Нажать при первом запуске, перед добавлением станций метро, локаций, и объектов доставки'
        ' чтобы бот не ругался на то, что Вы не закреплены за локацией\n',
        'Общие команды:',
        '2. /help - Получить справку',
        '3. /cart - Корзина',
        '4. /menu - Показать меню\n',
        'Команды админа:',
        '5. /publish_post - Создать промо пост',
        '6. /set_about - Добавить/изменить описание компании\n',
        'Работа с персоналом:',
        'Добавление:',
        '7. /add_admin - Добавть админа',
        '8. /add_seller_admin - Добавить админа локации',
        '9. /add_seller - Добавить продавца',
        '10. /add_courier - Добавить курьера',
        'Удаление:',
        '11. /delete_admin - Удалить админа',
        '12. /remove_seller_admin - Удалить админа локации',
        '13. /remove_seller - Удалить продавца',
        '14. /remove_courier - Удалить курьера',
        'Локации персонала:',
        '15. /reset_seller_admin_location - Открепить админа локации от локации',
        '16. /reset_seller_location - Открепить продавца от локации',
        '17. /reset_courier_location - Открепить курьера от локации',
        '18. /change_seller_admin_location - Привязать админа локации к другой локации',
        '19. /change_seller_location - Привязать продавца к другой локации',
        '20. /change_courier_location - Привязать курьера к другой локации\n',
        'Работа с локациями:',
        '21. /add_metro - Добавить станцию метро',
        '22. /add_newlocation - Добавить точку продаж',
        '23. /add_local_object - Добавить объект локальной доставки',
        '24. /delete_metro - Удалить станцию метро',
        '25. /delete_location - Удалить точку продаж',
        '26. /remove_local_object - Удалить объект локальной доставки',
        '27. /edit_metro - Редактировать метро\n',
        'Работа с категориями:',
        '28. /add_category - Добавить категорию товара',
        '29. /remove_category - Удалить категорию товара',
        '30. /remove_category_from_stock - Убрать категорию из меню',
        '31. /return_category_to_stock - Вернуть категорию в меню\n',
        'Работа с товарами:',
        '32. /add_item - Добавить товар',
        '33. /remove_item - Удалить товар',
        '34. /remove_item_from_stock - Убрать товар из меню',
        '35. /return_item_to_stock - Вернуть товар в меню',
        '36. /edit_item - Редактировать товар\n',
        'Работа с пользователями:',
        '37. /ban_user - Заблокировать пользователя',
        '38. /unban_user - Разблокировать пользователя',
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


@dp.callback_query_handler(text='cancel_order_menu', state=['*'])
async def cancel_order_menu(call: CallbackQuery, state: FSMContext):
    """cancel_order_menu"""
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Вы в главном меню',
                              reply_markup=menu_keyboard)


@dp.callback_query_handler(text='cancel_admin', state=['*'])
async def cancel_admin(call: CallbackQuery, state: FSMContext):
    """cancel_admin"""
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Операция прервана\n'
                              'Вы в главном меню',
                              reply_markup=menu_keyboard)
