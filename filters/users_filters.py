import logging

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


class IsDeliveryCourierMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на курьера в сообщении"""
        return await db.is_delivery_courier(message.from_user.id)


class IsCourierCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на курьера в коллбеках"""
        return await db.is_courier(call.from_user.id)


class IsClientMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на пользователя в сообщении"""
        return await db.is_client(message.from_user.id)


class IsClientCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на пользователя в коллбеках"""
        return await db.is_client(call.from_user.id)


class IsNotClientMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на пользователя в сообщении"""
        return not await db.is_client(message.from_user.id)


class IsNotClientCallback(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        """Проверка на пользователя в коллбеках"""
        return not await db.is_client(call.from_user.id)


class HasNoLocation(BoundFilter):
    async def check(self, message: types.Message):
        """Пользователи, у которых удалилась локация"""
        return not await db.has_location(message.from_user.id)


class HasNoLocalObject(BoundFilter):
    async def check(self, message: types.Message):
        """Пользователи, у которых удалилась локация"""
        return not await db.has_local_object(message.from_user.id)


class HasNoMetro(BoundFilter):
    async def check(self, message: types.Message):
        """Пользователи, у которых удалилась локация"""
        return not await db.has_metro(message.from_user.id)


class IsBanned(BoundFilter):
    async def check(self, message: types.Message):
        """Забаненые пользователи"""
        return await db.is_banned(message.from_user.id)


class SellerAdminHasLocationMessage(BoundFilter):
    async def check(self, message: types.Message):
        """Проверка на продовца-админа в сообщении"""
        return await db.has_location_seller_admin(message.from_user.id)
