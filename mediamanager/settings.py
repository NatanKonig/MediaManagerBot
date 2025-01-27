import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_name: str
    bot_token: str
    api_id: int
    api_hash: str
    target_chat: int
    target_channel: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
