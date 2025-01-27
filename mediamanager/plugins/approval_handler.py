from pyrogram import filters
from pyrogram.types import CallbackQuery

from mediamanager.bot import ClientBot
from mediamanager.managers.approval_manager import ApprovalManager

approval_service = ApprovalManager()


@ClientBot.on_callback_query(filters.regex(r"^(approve|reject)_"))
async def callback_handle_approval(client: ClientBot, callback_query: CallbackQuery):
    await approval_service.process_handle_approval(client, callback_query)
