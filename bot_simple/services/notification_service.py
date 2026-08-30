from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from app.config import config
from app.logger import setup_logger
import logging

logger = setup_logger("NotificationService")

class NotificationService:
    """Сервис уведомлений для админов и пользователей"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def notify_admins_new_request(self, user_name: str, telegram_id: int, admin_ids: list[int]):
        """Уведомляет всех админов о новой заявке с кнопками одобрения"""
        text = (
            f"🆕 **Новая заявка на доступ**\n\n"
            f"👤 Имя: {user_name}\n"
            f"🆔 Telegram ID: `{telegram_id}`\n\n"
            f"Одобрить пользователя?"
        )
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{telegram_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{telegram_id}")
            ]
        ])

        for admin_id in admin_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                logger.info(f"📨 Уведомление о заявке отправлено админу {admin_id}")
            except Exception as e:
                logger.error(f"❌ Не удалось отправить уведомление админу {admin_id}: {e}")

    async def notify_user_approved(self, telegram_id: int):
        """Уведомляет пользователя об одобрении"""
        text = (
            f"✅ **Ваша заявка одобрена!**\n\n"
            f"Добро пожаловать в PianoTechniciansClub!\n"
            f"Нажмите /start чтобы получить доступ к инструментам."
        )
        try:
            await self.bot.send_message(chat_id=telegram_id, text=text, parse_mode="Markdown")
            logger.info(f"📨 Пользователь {telegram_id} уведомлён об одобрении")
        except Exception as e:
            logger.error(f"❌ Не удалось уведомить пользователя {telegram_id}: {e}")

    async def notify_user_rejected(self, telegram_id: int):
        """Уведомляет пользователя об отклонении"""
        text = (
            f"❌ **Ваша заявка отклонена**\n\n"
            f"К сожалению, ваш запрос на вступление в клуб не был одобрен.\n"
            f"Если вы считаете это ошибкой, свяжитесь с поддержкой на сайте."
        )
        try:
            await self.bot.send_message(chat_id=telegram_id, text=text, parse_mode="Markdown")
            logger.info(f"📨 Пользователь {telegram_id} уведомлён об отклонении")
        except Exception as e:
            logger.error(f"❌ Не удалось уведомить пользователя {telegram_id}: {e}")

    async def notify_admins_user_approved(self, user_name: str, telegram_id: int, approved_by: str, admin_ids: list[int]):
        """Уведомляет всех админов, что пользователь одобрен"""
        text = f"✅ Пользователь **{user_name}** (`{telegram_id}`) одобрен администратором **{approved_by}**."

        for admin_id in admin_ids:
            try:
                await self.bot.send_message(chat_id=admin_id, text=text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"❌ Не удалось уведомить админа {admin_id}: {e}")