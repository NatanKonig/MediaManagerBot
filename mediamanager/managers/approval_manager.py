from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from mediamanager.bot import ClientBot
from mediamanager.settings import Settings
from mediamanager.logger import logger


class ApprovalManager:
    def __init__(self):
        self.settings: Settings = Settings()
        pass

    async def send_approval_message(
        self, client: ClientBot, media_key: str, sender_name: str
    ):
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
        except Exception as e:
            logger.error(f"Send approval message: {e}")
