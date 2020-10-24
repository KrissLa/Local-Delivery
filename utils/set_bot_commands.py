from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("help", "Получить справку"),
        types.BotCommand("cart", "Корзина"),
        types.BotCommand("menu", "Показать меню"),
        types.BotCommand("order_status", "Статус заказ"),
        types.BotCommand("bonus_order_status", "Статус бонусного заказа"),
        types.BotCommand("restart", "Бот завис и не реагирует на Ваши сообщения")
    ])