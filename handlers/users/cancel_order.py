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
