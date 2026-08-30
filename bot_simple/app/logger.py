import logging
import sys
from datetime import datetime


# ANSI коды цветов для терминала
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


class ColoredFormatter(logging.Formatter):
    """Кастомный форматтер с цветами и эмодзи"""

    # Маппинг уровней логирования на цвета и эмодзи
    LEVEL_STYLES = {
        logging.DEBUG: (Colors.GRAY, ""),
        logging.INFO: (Colors.GREEN, "✅"),
        logging.WARNING: (Colors.YELLOW, "⚠️"),
        logging.ERROR: (Colors.RED, "❌"),
        logging.CRITICAL: (Colors.BOLD + Colors.RED, "💀"),
    }

    def format(self, record):
        # Получаем стиль для уровня
        color, emoji = self.LEVEL_STYLES.get(record.levelno, (Colors.RESET, "•"))

        # Форматируем время
        log_time = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Собираем сообщение
        # Формат: [Время] Эмодзи Уровень | Сообщение
        header = f"{Colors.GRAY}[{log_time}]{Colors.RESET} {emoji} {color}{record.levelname:<8}{Colors.RESET}"

        # Если есть исключение, добавляем его
        if record.exc_info:
            record.exc_text = self.formatException(record.exc_info)

        msg = record.getMessage()

        # Добавляем отступ для многострочных сообщений
        if "\n" in msg:
            msg = msg.replace("\n", f"\n{' ' * 25}")

        return f"{header} {Colors.CYAN}|{Colors.RESET} {msg}"


def setup_logger(name: str = "PianoBot") -> logging.Logger:
    """Настраивает и возвращает красивый логгер"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Удаляем старые хендлеры, чтобы не дублировать при перезапуске
    if logger.handlers:
        logger.handlers.clear()

    # Хендлер для вывода в консоль
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())

    logger.addHandler(handler)

    # Приветственное сообщение
    logger.info(f"{Colors.BOLD}🤖 PianoTechnicians Bot запущен{Colors.RESET}")
    logger.info(f"{Colors.GRAY}{'=' * 50}{Colors.RESET}")

    return logger