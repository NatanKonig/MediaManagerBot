import sys
from pathlib import Path

from loguru import logger

logger.remove()
# LOGS_DIR = Path("log")
# LOGS_DIR.mkdir(parents=True, exist_ok=True)
FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)


logger.add(sys.stdout, format=FORMAT, level="DEBUG", colorize=True)

# logger.add(
#     LOGS_DIR / "app.log",
#     format=FORMAT,
#     level="DEBUG",
#     colorize=True,
#     rotation="49 MB",
#     retention="7 days",
#     encoding="utf-8",
# )

# https://chatgpt.com/c/6796ccb3-6910-8011-8f31-2925d9bfd0a2
