import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем .env из папки bot_simple
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, '..', 'backend', 'piano_club.db')}"
    AGE_DB_PATH: str = os.path.join(BASE_DIR, "..", "backend", "piano_age.db")

    # Telegram канал и чат
    CHANNEL_URL: str = os.getenv("CHANNEL_URL", "https://t.me/+uliQL4b7FPM0MGRi")
    CHAT_URL: str = os.getenv("CHAT_URL", "https://t.me/+ZkHOohtAqk05ZGVi")

    def validate(self):
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не задан в .env")


config = Config()