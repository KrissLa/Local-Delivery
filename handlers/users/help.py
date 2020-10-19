from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandHelp

from filters.users_filters import IsAdminMessage, IsSellerAdminMessage, IsSellerMessage, IsCourierMessage, \
    IsDeliveryCourierMessage
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
        '13. Добавить курьера оптовых заказов - /add_delivery_courier',
        '   Удаление:',
        '14. Удалить админа - /delete_admin',
        '15. Удалить админа локации - /remove_seller_admin',
        '16. Удалить продавца - /remove_seller',
        '17. Удалить курьера - /remove_courier',
        '18. Удалить курьера оптовых заказов - /remove_delivery_courier',
        '   Локации персонала:',
        '19. Открепить админа локации от локации - /reset_seller_admin_location',
        '20. Открепить продавца от локации - /reset_seller_location',
        '21. Открепить курьера от локации - /reset_courier_location',
        '22. Привязать админа локации к другой локации - /change_seller_admin_location',
        '23. Привязать продавца к другой локации - /change_seller_location',
        '24. Привязать курьера к другой локации - /change_courier_location\n',
        'Работа с локациями:',
        '25. Добавить станцию метро - /add_metro',
        '26. Добавить точку продаж - /add_newlocation',
        '27. Добавить объект локальной доставки - /add_local_object',
        '28. Удалить станцию метро - /delete_metro',
        '29. Удалить точку продаж - /delete_location',
        '30. Удалить объект локальной доставки - /remove_local_object',
        '31. Редактировать метро - /edit_metro\n',
        'Работа с категориями:',
        '32. Добавить категорию товара - /add_category',
        '33. Удалить категорию товара - /remove_category',
        '34. Убрать категорию из меню - /remove_category_from_stock',
        '35. Вернуть категорию в меню - /return_category_to_stock\n',
        'Работа с товарами:',
        '36. Добавить товар - /add_item',
        '37. Удалить товар - /remove_item',
        '38. Убрать товар из меню - /remove_item_from_stock',
        '39. Вернуть товар в меню - /return_item_to_stock',
        '40. Редактировать товар - /edit_item\n',
        'Работа с пользователями:',
        '41. Заблокировать пользователя - /ban_user',
        '42. Разблокировать пользователя - /unban_user\n',
        'Работа с оптовыми товарами:',
        '43. Добавить новую категорию для оптовых поставок - /add_delivery_category',
        '44. Добавить новый товар для оптовых поставок - /add_delivery_item',
        '45. Изменить цену товара для оптовых поставок - /edit_delivery_item_price\n',
        '46. Удалить категорию для оптовых поставок - /remove_delivery_category',
        '47. Удалить товар для оптовых поставок - /remove_delivery_item\n',
        '48. Убрать товар для оптовых поставок из меню - /remove_delivery_item_from_stock',
        '49. Вернуть товар для оптовых поставок в меню - /return_delivery_item_to_stock\n',

        'Работа с оптовыми заказами:',
        '50. Принять новые заказы - /take_orders',
        '51. Заказы, в которых не назначен курьер (Выбрать курьера для доставки заказа) - /delivery_order_set_courier',
        '52. Список заказов, ожидающих подтверждения курьером - /delivery_orders_awaiting_courier',
        '53. Список заказов, ожидающих доставки - /delivery_orders_awaiting_delivery\n',

        'Статистика:',
        '54. Получить статистику - /get_statistics',
        '54. Добавить/изменить email адрес для получения статистики - /update_email',
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
        'Статистика:',
        '16. Получить статистику - /get_statistics',
        '17. Добавить/изменить email адрес для получения статистики - /update_email',
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
@dp.message_handler(CommandHelp(), IsDeliveryCourierMessage(), state=states_for_menu)
@dp.message_handler(CommandHelp(), IsDeliveryCourierMessage(), state='*')
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
        '6. Начать принимать заказы - /im_at_work_dc',
        '7. Прекратить принимать заказы - /im_at_home_dc',
        '8. Список новых или измененных заказов, ожидающих подтверждения - /unaccepted_delivery_orders',
        '9. Список подтвержденных заказов, ожидающих доставки - /confirm_delivery_order',

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
        '6. Начать принимать заказы - /im_at_work_c',
        '7. Прекратить принимать заказы - /im_at_home_c',
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