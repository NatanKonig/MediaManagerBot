from pyrogram import filters
from pyrogram.types import Message

from mediamanager.bot import ClientBot
from mediamanager.managers.media_manager import MediaManager

media_service = MediaManager()


@ClientBot.on_message(
    (filters.photo | filters.video | filters.document | filters.audio | filters.voice)
    & filters.private
)
async def process_media_handler(client: ClientBot, message: Message):
    await media_service.process_message_with_media(client, message)
