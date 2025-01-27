from typing import Callable, Union

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from mediamanager.settings import Settings


class CustomFilters:
    def __init__(self):
        self.settings: Settings = Settings()

    def create_admin_filter(self) -> Callable:
        async def func(flt, client, update: Union[Message, CallbackQuery]):
            if isinstance(update, CallbackQuery):
                user_id = update.from_user.id
            else:
                user_id = update.from_user.id

            return user_id in self.settings.admin_ids

        return filters.create(func)

    @property
    def is_admin(self):
        return self.create_admin_filter()
