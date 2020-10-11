from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandHelp

from filters.users_filters import IsAdminMessage, IsSellerAdminMessage, IsSellerMessage, IsCourierMessage
from loader import dp
from utils.check_states import states_for_menu, reset_state
from utils.misc import rate_limit


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsAdminMessage(), state=states_for_menu)
@dp.message_handler(CommandHelp(), IsAdminMessage(), state='*')
async def bot_help(message: types.Message, state: FSMContext):
    await reset_state(state, message)
    text = [
        'Список команд: ',
        '0. Если бот завис и не реагирует на Ваши сообщения - /restart',
        '1. Нажать при первом запуске, перед добавлением станций метро, локаций, и объектов доставки'
        ' чтобы бот не ругался на то, что Вы не закреплены за локацией - /first_start\n',
        'Общие команды:',
        '2. Получить справку - /help',
        '3. Корзина - /cart',
        '4. Показать меню - /menu',
        '5. Показать статус заказа - /order_status',
        '6. Показать статус бонусного заказа - /bonus_order_status\n',
        'Команды админа:',
        '7. Создать промо пост - /publish_post',
        '8. Добавить/изменить описание компании - /set_about\n',
        'Работа с персоналом:',
        '   Добавление:',
        '9. Добавть админа - /add_admin',
        '10. Добавить админа локации - /add_seller_admin',
        '11. Добавить продавца - /add_seller',
        '12. Добавить курьера - /add_courier',
        '   Удаление:',
        '13. Удалить админа - /delete_admin',
        '14. Удалить админа локации - /remove_seller_admin',
        '15. Удалить продавца - /remove_seller',
        '16. Удалить курьера - /remove_courier',
        '   Локации персонала:',
        '17. Открепить админа локации от локации - /reset_seller_admin_location',
        '18. Открепить продавца от локации - /reset_seller_location',
        '19. Открепить курьера от локации - /reset_courier_location',
        '20. Привязать админа локации к другой локации - /change_seller_admin_location',
        '21. Привязать продавца к другой локации - /change_seller_location',
        '22. Привязать курьера к другой локации - /change_courier_location\n',
        'Работа с локациями:',
        '23. Добавить станцию метро - /add_metro',
        '24. Добавить точку продаж - /add_newlocation',
        '25. Добавить объект локальной доставки - /add_local_object',
        '26. Удалить станцию метро - /delete_metro',
        '27. Удалить точку продаж - /delete_location',
        '28. Удалить объект локальной доставки - /remove_local_object',
        '29. Редактировать метро - /edit_metro\n',
        'Работа с категориями:',
        '30. Добавить категорию товара - /add_category',
        '31. Удалить категорию товара - /remove_category',
        '32. Убрать категорию из меню - /remove_category_from_stock',
        '33. Вернуть категорию в меню - /return_category_to_stock\n',
        'Работа с товарами:',
        '34. Добавить товар - /add_item',
        '35. Удалить товар - /remove_item',
        '36. Убрать товар из меню - /remove_item_from_stock',
        '37. Вернуть товар в меню - /return_item_to_stock',
        '38. Редактировать товар - /edit_item\n',
        'Работа с пользователями:',
        '39. Заблокировать пользователя - /ban_user',
        '40. Разблокировать пользователя - /unban_user\n',
        'Работа с оптовыми товарами:',
        '41. Добавить новую категорию для оптовых поставок - /add_delivery_category',
        '42. Добавить новый товар для оптовых поставок - /add_delivery_item',
        '43. Изменить цену товара для оптовых поставок - /edit_delivery_item_price\n',
        '44. Удалить категорию для оптовых поставок - /remove_delivery_category',
        '45. Удалить товар для оптовых поставок - /remove_delivery_item\n',
        '46. Убрать товар для оптовых поставок из меню - /remove_delivery_item_from_stock',
        '47. Вернуть товар для оптовых поставок в меню - /return_delivery_item_to_stock\n',

        'Работа с оптовыми заказами:',
        '48. Принять новые или измененные заказы - /take_orders',
        '49. Подтвердить доставку заказа - /confirm_delivery',




    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsSellerAdminMessage(), state=states_for_menu)
@dp.message_handler(CommandHelp(), IsSellerAdminMessage(), state='*')
async def bot_help(message: types.Message, state: FSMContext):
    await reset_state(state, message)
    text = [
        'Общие команды: ',
        '0. Если бот завис и не реагирует на Ваши сообщения - /restart',
        '1. Получить справку - /help',
        '2. Корзина - /cart',
        '3. Показать меню - /menu',
        '4. Показать статус заказа - /order_status',
        '5. Показать статус бонусного заказа - /bonus_order_status\n',
        'Работа с персоналом:',
        '6. Добавить продавца - /add_new_seller',
        '7. Удалить продавца - /remove_sellers_',
        '8. Добавить курьера - /add_new_courier',
        '9. Удалить курьера - /remove_courier_\n',
        'Работа с меню:',
        '10. Убрать категорию из меню - /remove_category_from_stock',
        '11. Вернуть категорию в меню - /return_category_to_stock',
        '12. Убрать товар из меню - /remove_item_from_stock',
        '13. Вернуть товар в меню - /return_item_to_stock\n',
        'Работа с оптовыми заказами:',
        '14. Создать новый заказ на поставку - /new_delivery_order',
        '15. Посмотреть/изменить/отменить заказы на поставку - /change_delivery_order\n',
        'Статистика',
        '16. Получить статистику - /get_statistics'
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsSellerMessage(), state=states_for_menu)
@dp.message_handler(CommandHelp(), IsSellerMessage(), state='*')
async def bot_help(message: types.Message, state: FSMContext):
    await reset_state(state, message)
    text = [
        'Общие команды: ',
        '0. Если бот завис и не реагирует на Ваши сообщения - /restart',
        '1. Получить справку - /help',
        '2. Корзина - /cart',
        '3. Показать меню - /menu',
        '4. Показать статус заказа - /order_status',
        '5. Показать статус бонусного заказа - /bonus_order_status\n',
        'Команды продавца:',
        '6. Начать принимать заказы - /im_at_work',
        '7. Прекратить принимать заказы - /im_at_home',
        '8. Все непринятые заказы - /unaccepted_orders',
        '9. Все принятые заказы. Отмечать заказы как готовые здесь - /active_orders',
        '10. Подтверждение выдачи заказа - /confirm_delivery',
        '11. Бонусные непринятые  заказы -/unaccepted_bonus_orders'
        '12. Бонусные принятые заказы. Отмечать заказы как готовые здесь - /active_bonus_orders',
        '13. Подтверждение выдачи бонусного заказа - /confirm_bonus_delivery',
    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), IsCourierMessage(), state=states_for_menu)
@dp.message_handler(CommandHelp(), IsCourierMessage(), state='*')
async def bot_help(message: types.Message, state: FSMContext):
    await reset_state(state, message)
    text = [
        'Общие команды: ',
        '0. Если бот завис и не реагирует на Ваши сообщения - /restart',
        '1. Получить справку - /help',
        '2. Корзина - /cart',
        '3. Показать меню - /menu',
        '4. Показать статус заказа - /order_status',
        '5. Показать статус бонусного заказа - /bonus_order_status\n',
        'Команды курьера:',
        '6. Начать принимать заказы - /im_at_work',
        '7. Прекратить принимать заказы - /im_at_home',
        '8. Список заказов, готовых для доставки - /all_ready_orders',
        '9. Список заказов, закрепленных за Вами - /my_orders',

    ]
    await message.answer('\n'.join(text))


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp(), state=states_for_menu)
@dp.message_handler(CommandHelp(), state='*')
async def bot_help(message: types.Message, state: FSMContext):
    await reset_state(state, message)
    text = [
        'Список команд: ',
        '0. Если бот завис и не реагирует на Ваши сообщения - /restart',
        '1. Получить справку - /help',
        '2. Корзина - /cart',
        '3. Показать меню - /menu',
        '4. Показать статус заказа - /order_status',

    ]
    await message.answer('\n'.join(text))





########### /add_local_object admin, seller_admin
########### /delete_local_object admin, seller_admin


# /add_new_courier admin, seller_admin
# /remove_courier admin, seller_admin



#/remove_category_from_stock admin, seller_admin
#/return_category_to_stock admin, seller_admin



#/remove_item_from_stock admin, seller_admin
#/return_item_to_stock admin, seller_admin


# /add_new_seller admin, seller_admin
# /remove_sellers admin, seller_admin













#### /change_local_object admin, seller_admin


#### /change_category admin


#### /change_location admin










########### /add_admin admin
########### /delete_admin admin


########### /add_metro admin
########### /delete_metro admin


########### /add_newlocation admin
########### /delete_location admin


########### /add_local_object admin, seller_admin
########### /delete_local_object admin, seller_admin

########### /add_category admin
########### /remove_category admin


########## /add_item admin
########## /remove_item admin


########## /add_seller_admin admin
########## /remove_seller_admin admin

########## /reset_seller_admin_location admin


########## /add_seller admin, seller_admin
########## /remove_sellers admin, seller_admin

########## /reset_seller_location admin, seller_admin


######### /add_courier admin, seller_admin
######### /remove_courier admin, seller_admin

######### /reset_courier_location admin, seller_admin


######### /remove_category_from_stock admin, seller_admin
######### /return_category_to_stock admin, seller_admin



#########/remove_item_from_stock admin, seller_admin
######### /return_item_to_stock admin, seller_admin



######### /change_seller_admin_location admin


######### /change_seller_location admin


######### /change_courier_location admin


######### /edit_metro admin


####### /edit_item admin