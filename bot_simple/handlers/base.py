from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes


class BaseHandler(ABC):
    """Абстрактный базовый класс для всех обработчиков"""

    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основной метод обработки команды"""
        pass

    @abstractmethod
    def get_command(self) -> str:
        """Возвращает имя команды (например, 'start')"""
        pass