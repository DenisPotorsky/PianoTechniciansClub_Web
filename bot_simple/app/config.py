import os
from dataclasses import dataclass
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Единый путь к базе данных
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./data/piano_club.db")


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = DB_PATH

    # Оставляем для обратной совместимости со старым кодом
    AGE_DB_PATH: str = DB_PATH
    STRINGS_DB_PATH: str = DB_PATH

    CHANNEL_URL: str = os.getenv("CHANNEL_URL", "https://t.me/+uliQL4b7FPM0MGRi")
    CHAT_URL: str = os.getenv("CHAT_URL", "https://t.me/+ZkHOohtAqk05ZGVi")

    def validate(self):
        if not self.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN не задан в .env")
        if not self.DATABASE_URL:
            raise ValueError("❌ DATABASE_URL не задан")


config = Config()