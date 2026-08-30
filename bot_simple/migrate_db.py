"""
Скрипт миграции базы данных.
Запускается ОДИН РАЗ для создания недостающих таблиц.
"""
from app.database import engine, Base
from models.db_models import User, Calculation, Subscription  # Импортируем ВСЕ модели
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    logger.info(" Начинаю миграцию базы данных...")

    try:
        # create_all проверяет наличие таблиц и создает только те, которых нет
        Base.metadata.create_all(engine)
        logger.info("✅ Таблицы успешно созданы/проверены!")

        # Проверяем, что таблица subscriptions действительно существует
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'subscriptions' in tables:
            logger.info("📊 Таблица 'subscriptions' найдена в базе.")
        else:
            logger.error("❌ Таблица 'subscriptions' НЕ создана! Проверьте модели.")

        if 'calculations' in tables:
            logger.info(" Таблица 'calculations' найдена в базе.")
        else:
            logger.warning("️ Таблица 'calculations' отсутствует.")

    except Exception as e:
        logger.error(f"💀 Ошибка миграции: {e}", exc_info=True)


if __name__ == "__main__":
    migrate()