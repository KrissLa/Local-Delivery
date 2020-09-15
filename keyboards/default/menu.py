from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Меню'),
            KeyboardButton(text='Акции и бонусы'),
        ],
        [
            KeyboardButton(text='Профиль'),
            KeyboardButton(text='О сервисе')
        ]
    ],
    resize_keyboard=True
)
