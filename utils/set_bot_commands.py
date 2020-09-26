from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("help", "Получить справку"),
        types.BotCommand("cart", "Корзина"),
        types.BotCommand("menu", "Показать меню"),
        types.BotCommand("order_status", "Показать статус заказ")
    ])