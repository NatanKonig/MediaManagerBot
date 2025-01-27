from pyrogram import filters
from pyrogram.types import CallbackQuery

from mediamanager.bot import ClientBot
from mediamanager.managers.approval_manager import ApprovalManager


approval_service = ApprovalManager()


@ClientBot.on_callback_query(filters.regex(r"^(approve|reject)_"))
async def process_handle_approval(client: ClientBot, callback_query: CallbackQuery):
    action, message_id = callback_query.data.split("_")

    if action == "approve":
        # Encaminhar a mídia para o canal de destino
        await client.send_media_group(
            chat_id=approval_service.settings.target_channel,
            media=await client.get_media_group(callback_query.message.chat.id, message_id),
        )
        await callback_query.message.edit_text("✅ Mídia aprovada e enviada ao canal!")
    else:
        # Apenas rejeitar
        await callback_query.message.edit_text("❌ Mídia rejeitada.")
