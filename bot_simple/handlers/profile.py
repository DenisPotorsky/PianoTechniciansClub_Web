from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    MessageHandler, filters, CommandHandler
)
from handlers.base import BaseHandler
from handlers.start import get_nav_rows
from services.user_service import UserService
from services.access_service import AccessService
from services.notification_service import NotificationService
from services.user_management_service import UserManagementService
from app.database import SessionLocal
from models.db_models import Calculation
from sqlalchemy import func
from app.logger import setup_logger

logger = setup_logger("ProfileHandler")

EDIT_EMAIL, EDIT_PHONE, EDIT_CITY, EDIT_LASTNAME = range(4)


class ProfileHandler(BaseHandler):
    def __init__(self, user_service: UserService, access_service: AccessService,
                 notification_service: NotificationService, user_mgmt_service: UserManagementService):
        self.user_service = user_service
        self.access_service = access_service
        self.notification_service = notification_service
        self.user_mgmt_service = user_mgmt_service

    def get_command(self) -> str:
        return "profile"

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /profile"""
        await self.show_profile(update, context)

    def get_conversation_handler(self):
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.edit_lastname_start, pattern="^profile_edit_lastname$"),
                CallbackQueryHandler(self.edit_email_start, pattern="^profile_edit_email$"),
                CallbackQueryHandler(self.edit_phone_start, pattern="^profile_edit_phone$"),
                CallbackQueryHandler(self.edit_city_start, pattern="^profile_edit_city$"),
            ],
            states={
                EDIT_LASTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_lastname)],
                EDIT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_email)],
                EDIT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_phone)],
                EDIT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_city)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_edit)],
            name="profile_conv"
        )

    async def show_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает экран профиля"""
        query = update.callback_query if update.callback_query else None
        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)

        if not db_user:
            text = "❌ Профиль не найден."
            if query:
                await query.edit_message_text(text)
            else:
                await update.message.reply_text(text)
            return

        # Получаем статистику расчётов
        calc_count, last_calc_date = self._get_user_stats(db_user.id)

        status_text = "Супер-администратор" if db_user.is_super_admin else \
                      "Администратор" if db_user.is_admin else "Участник клуба"

        created_str = db_user.created_at.strftime("%d.%m.%Y") if db_user.created_at else "—"
        last_calc_str = last_calc_date.strftime("%d.%m.%Y") if last_calc_date else "—"

        text = (
            f"👤 **Ваш профиль**\n\n"
            f"Имя: {db_user.first_name or '—'}\n"
            f"Фамилия: {db_user.last_name or 'не указана'}\n"
            f"Email: {db_user.email or 'не указан'}\n"
            f"Телефон: {db_user.phone or 'не указан'}\n"
            f"Город: {db_user.city or 'не указан'}\n"
            f"Статус: {status_text}\n"
            f"В клубе с: {created_str}\n"
            f"Расчётов: {calc_count} (последний: {last_calc_str})"
        )

        rows = [
            [InlineKeyboardButton("✏️ Редактировать фамилию", callback_data="profile_edit_lastname")],
            [InlineKeyboardButton("✏️ Редактировать email", callback_data="profile_edit_email")],
            [InlineKeyboardButton("✏️ Редактировать телефон", callback_data="profile_edit_phone")],
            [InlineKeyboardButton("✏️ Редактировать город", callback_data="profile_edit_city")],
            [InlineKeyboardButton("🚪 Выйти из клуба", callback_data="profile_logout")],
            [InlineKeyboardButton("🗑️ Удалить профиль", callback_data="profile_delete_confirm")],
        ]
        rows.extend(get_nav_rows(include_back=False))

        reply_markup = InlineKeyboardMarkup(rows)
        if query:
            await query.answer()
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    def _get_user_stats(self, user_id: int):
        """Получает количество расчётов и дату последнего"""
        db = SessionLocal()
        try:
            count = db.query(func.count(Calculation.id)).filter(Calculation.user_id == user_id).scalar() or 0
            last = db.query(func.max(Calculation.created_at)).filter(Calculation.user_id == user_id).scalar()
            return count, last
        finally:
            db.close()

    # === РЕДАКТИРОВАНИЕ ===


    async def edit_lastname_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db_user = self.user_service.get_by_telegram_id(update.effective_user.id)
        current = db_user.last_name or "не указана"
        await query.edit_message_text(
            f"Текущая фамилия: {current}\n\nВведите новую фамилию:",
            reply_markup=InlineKeyboardMarkup(get_nav_rows(back_callback="profile_show"))
        )
        return EDIT_LASTNAME

    async def process_edit_lastname(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        new_lastname = update.message.text.strip()
        db_user = self.user_service.get_by_telegram_id(update.effective_user.id)
        
        # Обновляем через user_service
        from app.database import SessionLocal
        from models.db_models import User
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
            if user:
                user.last_name = new_lastname
                db.commit()
                await update.message.reply_text(f"✅ Фамилия обновлена: {new_lastname}")
            else:
                await update.message.reply_text("❌ Пользователь не найден")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
            db.rollback()
        finally:
            db.close()
        
        context.user_data.clear()
        return ConversationHandler.END

    async def edit_email_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db_user = self.user_service.get_by_telegram_id(update.effective_user.id)
        current = db_user.email or "не указан"
        await query.edit_message_text(
            f"Текущий email: {current}\n\nВведите новый email:",
            reply_markup=InlineKeyboardMarkup(get_nav_rows(back_callback="profile_show"))
        )
        return EDIT_EMAIL

    async def process_edit_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        new_value = update.message.text.strip()
        success = self._update_field(update.effective_user.id, "email", new_value)
        if success:
            await update.message.reply_text(f"✅ Email обновлён: {new_value}")
        else:
            await update.message.reply_text("❌ Ошибка обновления")
        return ConversationHandler.END

    async def edit_phone_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db_user = self.user_service.get_by_telegram_id(update.effective_user.id)
        current = db_user.phone or "не указан"
        await query.edit_message_text(
            f"Текущий телефон: {current}\n\nВведите новый телефон:",
            reply_markup=InlineKeyboardMarkup(get_nav_rows(back_callback="profile_show"))
        )
        return EDIT_PHONE

    async def process_edit_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        new_value = update.message.text.strip()
        success = self._update_field(update.effective_user.id, "phone", new_value)
        if success:
            await update.message.reply_text(f"✅ Телефон обновлён: {new_value}")
        else:
            await update.message.reply_text("❌ Ошибка обновления")
        return ConversationHandler.END

    async def edit_city_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db_user = self.user_service.get_by_telegram_id(update.effective_user.id)
        current = db_user.city or "не указан"
        await query.edit_message_text(
            f"Текущий город: {current}\n\nВведите новый город:",
            reply_markup=InlineKeyboardMarkup(get_nav_rows(back_callback="profile_show"))
        )
        return EDIT_CITY

    async def process_edit_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        new_value = update.message.text.strip()
        success = self._update_field(update.effective_user.id, "city", new_value)
        if success:
            await update.message.reply_text(f"✅ Город обновлён: {new_value}")
        else:
            await update.message.reply_text("❌ Ошибка обновления")
        return ConversationHandler.END

    def _update_field(self, telegram_id: int, field: str, value: str) -> bool:
        from models.db_models import User
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                setattr(user, field, value)
                db.commit()
                logger.info(f"✏️ Профиль обновлён: {field}={value} для {telegram_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка обновления профиля: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    async def cancel_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Отменено.")
        return ConversationHandler.END

    # === ВЫХОД ИЗ КЛУБА ===

    async def logout_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        rows = [
            [
                InlineKeyboardButton("🚪 Да, выйти", callback_data="profile_do_logout"),
                InlineKeyboardButton("❌ Отмена", callback_data="profile_show")
            ]
        ]
        await query.edit_message_text(
            "⚠️ **Вы уверены?**\n\n"
            "При выходе из клуба:\n"
            "• Все ваши расчёты будут удалены\n"
            "• Доступ к инструментам будет закрыт\n"
            "• Вы сможете подать заявку снова\n\n"
            "Продолжить?",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="Markdown"
        )

    async def do_logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)

        if not db_user:
            await query.edit_message_text("❌ Профиль не найден")
            return

        # Удаляем расчёты и сбрасываем права
        db = SessionLocal()
        try:
            db.query(Calculation).filter(Calculation.user_id == db_user.id).delete()
            db_user.is_approved = False
            db_user.is_admin = False
            db_user.is_super_admin = False
            db.commit()
            logger.info(f"🚪 Пользователь вышел из клуба: {user.first_name} ({user.id})")
        except Exception as e:
            logger.error(f"❌ Ошибка выхода: {e}")
            db.rollback()
            await query.edit_message_text("❌ Ошибка при выходе")
            return
        finally:
            db.close()

        # Уведомляем админов
        admin_ids = self.user_mgmt_service.get_admin_ids()
        for admin_id in admin_ids:
            try:
                await self.notification_service.bot.send_message(
                    chat_id=admin_id,
                    text=f"🚪 Пользователь **{user.first_name}** (`{user.id}`) вышел из клуба.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

        await query.edit_message_text(
            "🚪 **Вы вышли из клуба.**\n\n"
            "Ваши расчёты удалены.\n"
            "Вы можете подать заявку на вступление снова через /start."
        )

    # === УДАЛЕНИЕ ПРОФИЛЯ ===

    async def delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        rows = [
            [
                InlineKeyboardButton("⚠️ Да, удалить", callback_data="profile_delete_final"),
                InlineKeyboardButton("❌ Отмена", callback_data="profile_show")
            ]
        ]
        await query.edit_message_text(
            "🗑️ **УДАЛЕНИЕ ПРОФИЛЯ**\n\n"
            "Это действие **необратимо**!\n\n"
            "Будут удалены:\n"
            "• Все ваши данные\n"
            "• Все расчёты\n"
            "• История подписок\n\n"
            "Вы точно хотите удалить профиль?",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="Markdown"
        )

    async def delete_final(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)

        if not db_user:
            await query.edit_message_text("❌ Профиль не найден")
            return

        # Полное удаление (cascade удалит расчёты и подписки)
        db = SessionLocal()
        try:
            db.delete(db_user)
            db.commit()
            logger.info(f"🗑️ Профиль удалён: {user.first_name} ({user.id})")
        except Exception as e:
            logger.error(f"❌ Ошибка удаления: {e}")
            db.rollback()
            await query.edit_message_text("❌ Ошибка при удалении")
            return
        finally:
            db.close()

        # Уведомляем админов
        admin_ids = self.user_mgmt_service.get_admin_ids()
        for admin_id in admin_ids:
            try:
                await self.notification_service.bot.send_message(
                    chat_id=admin_id,
                    text=f"🗑️ Пользователь **{user.first_name}** (`{user.id}`) удалил свой профиль.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

        await query.edit_message_text(
            "🗑️ **Профиль удалён.**\n\n"
            "Все ваши данные стёрты.\n"
            "Вы можете зарегистрироваться снова через /start."
        )