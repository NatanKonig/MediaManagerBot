import asyncio

from pyrogram import Client
from pyrogram.sync import idle

from mediamanager.logger import logger
from mediamanager.settings import Settings


class ClientBot(Client):

    def __init__(self):
        settings = Settings()
        super().__init__(
            name=settings.bot_name,
            api_id=settings.api_id,
            api_hash=settings.api_hash,
            bot_token=settings.bot_token,
            plugins=dict(root="mediamanager/plugins/"),
        )


async def main():
    client = ClientBot()
    await client.start()
    await idle()


if __name__ == "__main__":
    try:
        logger.success("Bot iniciado!")
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
        exit(1)
    except KeyboardInterrupt:
        logger.warning("Bot finalizado!")
        exit(0)
