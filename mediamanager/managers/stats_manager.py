import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from pyrogram.types import User


class StatsManager:
    def __init__(self):
        self.file_path = "stats.json"
        self.stats = self._load_stats()

    def _load_stats(self) -> bool:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    self.stats = json.load(file)
                    return True
            except json.JSONDecodeError:
                return False
        return False

    def _save_stats(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.stats, file, indent=4, ensure_ascii=False)

    def _format_user_mention(self, user_data: Dict[str, Any]) -> str:
        if user_data.get("username"):
            return f"@{user_data['username']}"
        return f"[{user_data['first_name']}](tg://user?id={user_data['user_id']})"

    def update_user_stats(
        self, user: User, media_type: str = "media", count: int = 1
    ) -> None:
        self._load_stats()
        user_id = str(user.id)
        if user_id not in self.stats:
            self.stats[user_id] = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "media_count": 0,
                "media_types": {},
            }

        self.stats[user_id].update(
            {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )

        self.stats[user_id]["media_count"] += count
        if media_type not in self.stats[user_id]["media_types"]:
            self.stats[user_id]["media_types"][media_type] = 0
        self.stats[user_id]["media_types"][media_type] += count
        self._save_stats()

    def get_stats_message(self) -> str:
        self._load_stats()
        if not self.stats:
            return "📊 Nenhuma estatística disponível."

        stats_message = "📊 **Estatísticas de Envios**\n\n"

        sorted_users = sorted(
            self.stats.items(), key=lambda x: x[1]["media_count"], reverse=True
        )

        total_media = 0
        for user_id, data in sorted_users:
            total_media += data["media_count"]
            user_mention = self._format_user_mention(data)

            media_types = []
            for media_type, count in data["media_types"].items():
                media_types.append(f"{media_type}: {count}")

            stats_message += (
                f"👤 {user_mention}\n"
                f"├ Total: {data['media_count']} mídias\n"
                f"└ Tipos: {', '.join(media_types)}\n"
            )

        stats_message += f"\n📈 **Total Geral:** {total_media} mídias enviadas"
        return stats_message

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        user_id = str(user_id)
        return self.stats.get(
            user_id,
            {
                "user_id": user_id,
                "username": None,
                "first_name": "Desconhecido",
                "last_name": None,
                "media_count": 0,
                "media_types": {},
            },
        )

    def _format_date(self, date_str: Optional[str]) -> str:
        if not date_str:
            return "Nunca"
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return "Data inválida"

    def get_user_detailed_stats(self, user_id: int) -> str:
        stats = self.get_user_stats(user_id)
        if not stats["media_count"]:
            return "📊 Este usuário ainda não enviou nenhuma mídia."

        user_mention = self._format_user_mention(stats)
        message = f"📊 **Estatísticas Detalhadas**\n\n"
        message += f"👤 **Usuário:** {user_mention}\n"

        if stats["first_name"]:
            name_parts = [stats["first_name"]]
            if stats["last_name"]:
                name_parts.append(stats["last_name"])
            message += f"📝 **Nome:** {' '.join(name_parts)}\n"

        message += f"📤 **Total de Envios:** {stats['media_count']}\n"

        if stats["media_types"]:
            message += "\n📎 **Tipos de Mídia:**\n"
            for media_type, count in stats["media_types"].items():
                message += f"├ {media_type}: {count}\n"

        return message
