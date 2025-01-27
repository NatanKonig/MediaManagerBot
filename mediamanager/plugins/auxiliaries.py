from pyrogram import filters
from pyrogram.types import Message

from mediamanager.bot import ClientBot


@ClientBot.on_message(filters.command("info"))
async def simple_informations_command(client: ClientBot, message: Message):
    await message.reply(f"Id do grupo: {message.chat.id}")
