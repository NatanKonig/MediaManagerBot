from pyrogram.types import InputMediaPhoto, InputMediaVideo, Message

from mediamanager.bot import ClientBot
from mediamanager.logger import logger
from mediamanager.settings import Settings
from mediamanager.managers.approval_manager import ApprovalManager


class MediaManager:
    def __init__(self):
        self.settings: Settings = Settings()
        self.media_log_file = "media_submission.json"
        self.processed_media_groups: set[int] = set()
        self.approval_manager = ApprovalManager()

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

        for i, msg in enumerate(media_group):
            caption = (
                f"{msg.caption or ''}\n\nBy: {
                    formatted_name}"
                if i == 0
                else msg.caption
            )

            if msg.photo:
                media_list.append(
                    InputMediaPhoto(media=msg.photo.file_id, caption=caption)
                )
            elif msg.video:
                media_list.append(
                    InputMediaVideo(media=msg.video.file_id, caption=caption)
                )

        # Send media group
        sent_media = await client.send_media_group(
            chat_id=self.settings.target_chat, media=media_list
        )

        media_key = f"{message.media_group_id}"

        await self.approval_manager.send_approval_message(
            client, media_key, formatted_name
        )

    async def process_single_media(
        self, client: ClientBot, message: Message, formatted_name: str
    ) -> None:
        media_list = []
        media_methods = {
            "photo": (message.photo, InputMediaPhoto),
            "video": (message.video, InputMediaVideo),
            "document": (message.document, InputMediaPhoto),
            "audio": (message.audio, InputMediaPhoto),
            "voice": (message.voice, InputMediaPhoto),
        }

        for media_type, (media, media_class) in media_methods.items():
            if media:
                caption = f"{message.caption}\n\nEnviado por: {formatted_name}"
                media_list.append(media_class(
                    media=media.file_id, caption=caption))
                break

        # Send media to target group
        sent_media = await client.send_media_group(
            chat_id=self.settings.target_chat, media=media_list
        )

        media_key = f"single_media_{message.id}"

        # Send approval message for this media
        await self.approval_manager.send_approval_message(
            client, media_key, formatted_name
        )

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
