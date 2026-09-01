import sqlite3
import os
from unidecode import unidecode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    CommandHandler
)
from handlers.base import BaseHandler
from handlers.start import get_nav_rows
from services.user_service import UserService
from app.config import config
from app.logger import setup_logger

logger = setup_logger("RegulatingHandler")

REG_BRAND, REG_MODEL = range(2)


def normalize(text: str) -> str:
    if not text:
        return ""
    return unidecode(text).lower().strip()


class RegulatingHandler(BaseHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.db_path = os.path.join(os.path.dirname(config.AGE_DB_PATH), "piano_club.db")

    def get_command(self) -> str:
        return "reg"

    def get_conversation_handler(self):
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start, pattern="^reg_start$"),
                CommandHandler("reg", self.start)
            ],
            states={
                REG_BRAND: [CallbackQueryHandler(self.select_brand, pattern="^reg_brand_")],
                REG_MODEL: [CallbackQueryHandler(self.select_model, pattern="^reg_model_")],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                CallbackQueryHandler(self.nav_to_main_menu, pattern="^back_menu$"),
                CallbackQueryHandler(self.nav_back_to_start, pattern="^reg_start$"),
            ],
            name="regulating_conv"
        )

    async def nav_back_to_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        await self.start(update, context)
        return REG_BRAND

    async def nav_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        query = update.callback_query
        if query:
            await query.answer()
        from app.config import config as cfg
        from services.access_service import AccessService

        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)

        rows = [
            [InlineKeyboardButton("🧮 Калькулятор струн", callback_data="calc_start")],
            [InlineKeyboardButton("📅 Возраст фортепиано", callback_data="age_start")],
            [InlineKeyboardButton("📏 Мензуры", callback_data="mensur_start")],
            [InlineKeyboardButton("🔧 Регулировка", callback_data="reg_start")],
            [InlineKeyboardButton("👤 Мой профиль", callback_data="profile_show")],
            [InlineKeyboardButton("🌐 Сайт клуба", url="https://piano-technicians.club")],
        ]
        access_service = AccessService()
        if access_service.is_admin_panel_visible(db_user):
            role_icon = "" if db_user.is_super_admin else "️"
            rows.append([InlineKeyboardButton(f"{role_icon} Панель управления", callback_data="admin_panel")])
        rows.append([InlineKeyboardButton("ℹ️ О клубе", callback_data="about")])

        status_text = "Супер-администратор" if db_user and db_user.is_super_admin else \
                      "Администратор" if db_user and db_user.is_admin else "Участник клуба"

        text = (
            f"Привет, {user.first_name}! 👋\n\n"
            f"Добро пожаловать в **PianoTechniciansClub**.\n"
            f"✅ Статус: {status_text}\n\n"
            f"Выберите инструмент:"
        )

        if query:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
        return ConversationHandler.END

    def get_db_connection(self):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"База не найдена: {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        conn.create_function("normalize", 1, lambda x: normalize(x))
        conn.execute("PRAGMA case_sensitive_like = OFF")
        return conn

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT brand FROM regulating_params ORDER BY brand")
            brands = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logger.error(f"❌ Ошибка чтения брендов: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text(f"Ошибка базы данных: {e}")
            else:
                await update.message.reply_text(f"Ошибка базы данных: {e}")
            return ConversationHandler.END

        context.user_data['brands'] = brands

        rows = []
        for i, brand in enumerate(brands):
            rows.append([InlineKeyboardButton(brand, callback_data=f"reg_brand_{i}")])
        rows.extend(get_nav_rows(include_back=False))

        text = "🔧 **Регулировочные параметры**\n\nВыберите бренд:"

        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
        return REG_BRAND

    async def select_brand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        idx = int(query.data.split("_")[2])
        brands = context.user_data.get('brands', [])

        if idx >= len(brands):
            await query.answer("❌ Ошибка выбора", show_alert=True)
            return REG_BRAND

        selected_brand = brands[idx]
        context.user_data['selected_brand'] = selected_brand

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT model FROM regulating_params WHERE brand = ? ORDER BY model",
                (selected_brand,)
            )
            models = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logger.error(f"❌ Ошибка чтения моделей: {e}")
            await query.edit_message_text(f"Ошибка: {e}")
            return ConversationHandler.END

        context.user_data['models'] = models

        # Если модель одна — сразу показываем параметры
        if len(models) == 1:
            context.user_data['selected_model'] = models[0]
            await self._show_params(query, context)
            return ConversationHandler.END

        rows = []
        for i, model in enumerate(models):
            rows.append([InlineKeyboardButton(model, callback_data=f"reg_model_{i}")])
        rows.extend(get_nav_rows(back_callback="reg_start"))

        await query.edit_message_text(
            f"🎹 **{selected_brand}**\n\nВыберите модель:",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="Markdown"
        )
        return REG_MODEL

    async def select_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        idx = int(query.data.split("_")[2])
        models = context.user_data.get('models', [])

        if idx >= len(models):
            await query.answer("❌ Ошибка выбора", show_alert=True)
            return REG_MODEL

        context.user_data['selected_model'] = models[idx]
        await self._show_params(query, context)
        return ConversationHandler.END

    async def _show_params(self, query, context: ContextTypes.DEFAULT_TYPE):
        brand = context.user_data.get('selected_brand', '')
        model = context.user_data.get('selected_model', '')

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT parameter, value, unit FROM regulating_params 
                   WHERE brand = ? AND model = ? ORDER BY parameter""",
                (brand, model)
            )
            params = cursor.fetchall()
            conn.close()

            if not params:
                text = f"❗ Параметры для **{brand} — {model}** не найдены."
                logger.warning(f"⚠️ Параметры не найдены: {brand} {model}")
            else:
                text = f"🔧 **{brand} — {model}**\n"
                text += f"📋 {len(params)} параметров:\n\n"

                # Группируем параметры по категориям для удобства чтения
                for parameter, value, unit in params:
                    unit_str = f" {unit}" if unit else ""
                    text += f"• {parameter}: **{value}**{unit_str}\n"

                logger.info(f"✅ Показано {len(params)} параметров для {brand} {model}")

            rows = [
                [InlineKeyboardButton("🔄 Новый поиск", callback_data="reg_start")],
            ]
            rows.extend(get_nav_rows(include_back=False))

            # Telegram ограничивает сообщение 4096 символами
            if len(text) > 4000:
                # Разбиваем на части
                chunks = self._split_text(text, 3900)
                await query.edit_message_text(chunks[0], reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
                for chunk in chunks[1:]:
                    await query.message.reply_text(chunk, parse_mode="Markdown")
            else:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

        except Exception as e:
            logger.error(f"❌ Ошибка показа параметров: {e}", exc_info=True)
            await query.edit_message_text(f"Ошибка: {e}")

    @staticmethod
    def _split_text(text: str, max_len: int) -> list[str]:
        """Разбивает длинный текст на части по строкам"""
        lines = text.split("\n")
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 > max_len:
                chunks.append(current)
                current = line
            else:
                current = current + "\n" + line if current else line
        if current:
            chunks.append(current)
        return chunks

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Отменено.")
        context.user_data.clear()
        return ConversationHandler.END

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.start(update, context)