from pyrogram import filters
from pyrogram.types import Message

from mediamanager.bot import ClientBot
from mediamanager.managers.stats_manager import StatsManager
from mediamanager.plugins.custom_filters import CustomFilters

stats_service = StatsManager()
custom_filters = CustomFilters()


@ClientBot.on_message(filters.command("stats") & custom_filters.is_admin)
async def send_stats(client: ClientBot, message: Message):
    stats_message = stats_service.get_stats_message()
    await message.reply(stats_message)
