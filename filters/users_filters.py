from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from loader import db


class IsAdminMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на суперадмина в сообщении"""
        return await db.is_admin(message.from_user.id)


class IsAdminCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на суперадмина в коллбеках"""
        return await db.is_admin(call.from_user.id)


class IsSellerAdminMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на продовца-админа в сообщении"""
        return await db.is_seller_admin(message.from_user.id)


class IsSellerAdminCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на продовца-админа в коллбеках"""
        return await db.is_seller_admin(call.from_user.id)


class IsSellerMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на продовца в сообщении"""
        return await db.is_seller(message.from_user.id)


class IsSellerCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на продовца в коллбеках"""
        return await db.is_seller(call.from_user.id)


class IsCourierMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на курьера в сообщении"""
        return await db.is_courier(message.from_user.id)


class IsCourierCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на курьера в коллбеках"""
        return await db.is_courier(call.from_user.id)


class IsClientMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на курьера в сообщении"""
        return await db.is_client(message.from_user.id)


class IsClientCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на курьера в коллбеках"""
        return await db.is_client(call.from_user.id)
