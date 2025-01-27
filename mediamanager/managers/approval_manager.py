import asyncio
from queue import Queue

from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
)

from mediamanager.bot import ClientBot
from mediamanager.logger import logger
from mediamanager.settings import Settings
from mediamanager.utils import clean_caption


class ApprovalManager:
    def __init__(self):
        self.settings: Settings = Settings()
        self.approvals_queue: Queue = Queue()
        self.tasks = [asyncio.create_task(self.process_approvals_queue())]

    async def process_approvals_queue(self):
        while True:
            if not self.approvals_queue.empty():
                client, media_list = self.approvals_queue.get()
                for target_channel in self.settings.target_channel:
                    try:
                        await client.send_media_group(
                            chat_id=target_channel,
                            media=media_list,
                        )
                    except FloodWait as e:
                        wait_time = e.value
                        logger.warning(
                            f"FloodWait ao enviar grupo de mídia aprovada: aguardando {
                                wait_time} segundos antes de tentar novamente."
                        )
                        await asyncio.sleep(wait_time)
                    except Exception as e:
                        logger.error(f"Erro ao enviar grupo de mídia aprovada: {e}")

            await asyncio.sleep(5)

    async def send_approval_message(
        self, client: ClientBot, media_key: str, sender_name: str
    ):
        while True:
            try:
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "✅ Aprovar", callback_data=f"approve_{media_key}"
                            ),
                            InlineKeyboardButton(
                                "❌ Recusar", callback_data=f"reject_{media_key}"
                            ),
                        ]
                    ]
                )

                await client.send_message(
                    chat_id=self.settings.target_chat,
                    text=f"📥 Nova mídia enviada por {sender_name}. Aprovar?",
                    reply_markup=keyboard,
                )
                break
            except FloodWait as e:
                wait_time = e.value
                logger.warning(
                    f"FloodWait detectado: aguardando {
                        wait_time} segundos antes de tentar novamente."
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem de aprovação: {e}")
                break

    async def process_handle_approval(
        self, client: ClientBot, callback_query: CallbackQuery
    ):
        data_parts = callback_query.data.split("_")
        action = data_parts[0]
        chat_id = int(data_parts[1])
        message_id = int(data_parts[2])

        try:
            message = await client.get_messages(chat_id, message_id)
        except Exception as e:
            logger.error(f"Erro ao buscar mensagem: {e}")
            await callback_query.message.edit_text("⚠️ Erro ao processar a mídia.")
            return

        if message.caption:
            message.caption = await clean_caption(message.caption)

        if action == "approve":
            if message.media_group_id:
                media_group = await client.get_media_group(chat_id, message_id)
                media_list = []

                for msg in media_group:
                    if msg.caption:
                        msg.caption = await clean_caption(msg.caption)

                    if msg.photo:
                        media_list.append(
                            InputMediaPhoto(
                                media=msg.photo.file_id, caption=msg.caption
                            )
                        )
                    elif msg.video:
                        media_list.append(
                            InputMediaVideo(
                                media=msg.video.file_id, caption=msg.caption
                            )
                        )
                self.approvals_queue.put((client, media_list))
            else:
                if message.caption:
                    message.caption = await clean_caption(message.caption)

                if message.photo:
                    media = InputMediaPhoto(
                        media=message.photo.file_id, caption=message.caption
                    )
                elif message.video:
                    media = InputMediaVideo(
                        media=message.video.file_id, caption=message.caption
                    )
                else:
                    await callback_query.message.edit_text(
                        "⚠️ Tipo de mídia não suportado."
                    )
                    return

                self.approvals_queue.put((client, [media]))
            new_text = f"✅ Mídia aprovada por {
                callback_query.from_user.mention}."
            if callback_query.message.text != new_text:
                await callback_query.message.edit_text(new_text)
        else:
            new_text = f"❌ Mídia rejeitada por {
                callback_query.from_user.mention}."
            if callback_query.message.text != new_text:
                await callback_query.message.edit_text(new_text)
