import asyncio
from queue import Queue

from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaPhoto, InputMediaVideo, Message

from mediamanager.bot import ClientBot
from mediamanager.logger import logger
from mediamanager.managers.approval_manager import ApprovalManager
from mediamanager.managers.stats_manager import StatsManager
from mediamanager.settings import Settings


class MediaManager:
    def __init__(self):
        self.settings: Settings = Settings()
        self.processed_media_groups: set[int] = set()
        self.approval_manager: ApprovalManager = ApprovalManager()
        self.media_queue: Queue = Queue()
        self.tasks = [asyncio.create_task(self.process_media_queue())]
        self.stats_manager = StatsManager()

    async def process_media_queue(self):
        while True:
            if not self.media_queue.empty():
                client, media_list, formatted_name = self.media_queue.get()
                try:
                    sent_media = await client.send_media_group(
                        chat_id=self.settings.target_chat,
                        media=media_list,
                    )
                    media_key = f"{sent_media[0].chat.id}_{sent_media[0].id}"
                    await self.approval_manager.send_approval_message(
                        client, media_key, formatted_name
                    )
                except FloodWait as e:
                    wait_time = e.value
                    logger.warning(
                        f"FloodWait ao enviar grupo de mídia: aguardando {
                            wait_time} segundos antes de tentar novamente."
                    )
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    logger.error(f"Erro ao enviar grupo de mídia: {e}")

            await asyncio.sleep(5)

    async def process_message_with_media(
        self, client: ClientBot, message: Message
    ) -> None:
        try:
            formatted_name = self.get_format_name_from_msg(message)
            if message.media_group_id:
                await self.process_media_group(client, message, formatted_name)
            else:
                await self.process_single_media(client, message, formatted_name)
        except Exception as e:
            logger.error(f"Erro ao processar mídia: {e}")
            await message.reply("❌ Ocorreu um erro ao processar a mídia!")

    async def process_media_group(
        self, client: ClientBot, message: Message, formatted_name: str
    ) -> None:
        if message.media_group_id in self.processed_media_groups:
            return  # Ignore if already processed

        self.processed_media_groups.add(message.media_group_id)

        media_group = await client.get_media_group(message.chat.id, message.id)
        media_list = []

        photo_count = 0
        video_count = 0

        for i, msg in enumerate(media_group):
            caption = (
                f"{msg.caption or ''}\n\nBy: {
                    formatted_name}"
                if i == 0
                else msg.caption
            )

            if msg.photo:
                photo_count += 1
                media_list.append(
                    InputMediaPhoto(media=msg.photo.file_id, caption=caption)
                )
            elif msg.video:
                video_count += 1
                media_list.append(
                    InputMediaVideo(media=msg.video.file_id, caption=caption)
                )
        if photo_count > 0:
            self.stats_manager.update_user_stats(
                message.from_user, "photo", photo_count
            )
        if video_count > 0:
            self.stats_manager.update_user_stats(
                message.from_user, "video", video_count
            )
        self.media_queue.put((client, media_list, formatted_name))
        await message.reply("✅ Mídia recebida com sucesso!")

    async def process_single_media(
        self, client: ClientBot, message: Message, formatted_name: str
    ) -> None:
        media_mapping = {
            "photo": (message.photo, InputMediaPhoto),
            "video": (message.video, InputMediaVideo),
            "document": (message.document, InputMediaPhoto),
            "audio": (message.audio, InputMediaPhoto),
            "voice": (message.voice, InputMediaPhoto),
        }
        media_type, (media, media_class) = next(
            ((type_, data) for type_, data in media_mapping.items() if data[0]),
            (None, (None, None)),
        )
        if media_type:
            caption = f"{message.caption or ''}\n\nBy: {formatted_name}"
            media_item = media_class(media=media.file_id, caption=caption)

            self.stats_manager.update_user_stats(message.from_user, media_type)
            self.media_queue.put((client, [media_item], formatted_name))
            await message.reply("✅ Mídia recebida com sucesso!")

    def get_format_name_from_msg(self, message: Message) -> str:
        """
        Extract sender name from message

        :param message: Incoming message
        :return: Formatted sender name
        """
        if not message.from_user:
            return "Usuário Anônimo"

        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        username = (
            f"@{message.from_user.username}" if message.from_user.username else ""
        )
        return f"{first_name} {last_name} - {username}".strip()
