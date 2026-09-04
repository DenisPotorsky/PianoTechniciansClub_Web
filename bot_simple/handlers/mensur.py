import sqlite3
import os
from unidecode import unidecode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    MessageHandler, filters, CommandHandler
)
from handlers.base import BaseHandler
from handlers.start import get_nav_rows
from services.user_service import UserService
from app.config import config
from app.logger import setup_logger

logger = setup_logger("MensurHandler")

MENSUR_BRAND, MENSUR_MODEL, MENSUR_CHOR = range(3)

STRINGS_DB_PATH = config.STRINGS_DB_PATH


def normalize(text: str) -> str:
    if not text:
        return ""
    return unidecode(text).lower().strip()


class MensurHandler(BaseHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.db_path = "/app/data/piano_club.db"

    def get_command(self) -> str:
        return "mensur"

    def get_conversation_handler(self):
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start, pattern="^mensur_start$"),
                CommandHandler("mensur", self.start)
            ],
            states={
                MENSUR_BRAND: [CallbackQueryHandler(self.select_brand, pattern="^mensur_brand_")],
                MENSUR_MODEL: [CallbackQueryHandler(self.select_model, pattern="^mensur_model_")],
                MENSUR_CHOR: [CallbackQueryHandler(self.select_chor, pattern="^mensur_chor_")],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                CallbackQueryHandler(self.nav_to_main_menu, pattern="^back_menu$"),
                CallbackQueryHandler(self.nav_back_to_start, pattern="^mensur_start$"),
            ],
            name="mensur_conv"
        )

    async def nav_back_to_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        await self.start(update, context)
        return MENSUR_BRAND

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
            [InlineKeyboardButton("👤 Мой профиль", callback_data="profile_show")],  # ← ДОБАВИТЬ
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
            raise FileNotFoundError(f"База мензур не найдена: {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        conn.create_function("normalize", 1, lambda x: normalize(x))
        conn.execute("PRAGMA case_sensitive_like = OFF")
        return conn

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT brand FROM scales ORDER BY brand")
            brands = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logger.error(f"❌ Ошибка чтения брендов: {e}")
            await update.message.reply_text(f"Ошибка базы данных: {e}")
            return ConversationHandler.END

        rows = []
        for i, brand in enumerate(brands):
            rows.append([InlineKeyboardButton(brand, callback_data=f"mensur_brand_{i}")])

        # Сохраняем список брендов в контексте
        context.user_data['brands'] = brands

        rows.extend(get_nav_rows(include_back=False))
        keyboard = InlineKeyboardMarkup(rows)

        text = "📏 **Мензуры фортепианных струн**\n\nВыберите бренд:"

        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return MENSUR_BRAND

    async def select_brand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        idx = int(query.data.split("_")[2])
        brands = context.user_data.get('brands', [])

        if idx >= len(brands):
            await query.answer("❌ Ошибка выбора", show_alert=True)
            return MENSUR_BRAND

        selected_brand = brands[idx]
        context.user_data['selected_brand'] = selected_brand

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT model FROM scales WHERE brand = ? ORDER BY model",
                (selected_brand,)
            )
            models = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logger.error(f"❌ Ошибка чтения моделей: {e}")
            await query.edit_message_text(f"Ошибка: {e}")
            return ConversationHandler.END

        context.user_data['models'] = models

        rows = []
        for i, model in enumerate(models):
            rows.append([InlineKeyboardButton(model, callback_data=f"mensur_model_{i}")])
        rows.extend(get_nav_rows(back_callback="mensur_start"))

        await query.edit_message_text(
            f"🎹 **{selected_brand}**\n\nВыберите модель:",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="Markdown"
        )
        return MENSUR_MODEL

    async def select_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        idx = int(query.data.split("_")[2])
        models = context.user_data.get('models', [])
        brand = context.user_data.get('selected_brand', '')

        if idx >= len(models):
            await query.answer("❌ Ошибка выбора", show_alert=True)
            return MENSUR_MODEL

        selected_model = models[idx]
        context.user_data['selected_model'] = selected_model

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT DISTINCT chor_nummer
                   FROM scales
                   WHERE brand = ?
                     AND model = ?
                   ORDER BY chor_nummer""",
                (brand, selected_model)
            )
            chors = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logger.error(f"❌ Ошибка чтения хоров: {e}")
            await query.edit_message_text(f"Ошибка: {e}")
            return ConversationHandler.END

        context.user_data['chors'] = chors

        # Если хор один — сразу показываем результат
        if len(chors) == 1:
            context.user_data['selected_chor'] = chors[0]
            await self._show_result(query, context)
            return ConversationHandler.END

        rows = []
        for chor in chors:
            rows.append([InlineKeyboardButton(f"Хор {chor}", callback_data=f"mensur_chor_{chor}")])
        rows.extend(get_nav_rows(back_callback="mensur_start"))

        await query.edit_message_text(
            f"🎹 **{brand} — {selected_model}**\n\nВыберите номер хора:",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode="Markdown"
        )
        return MENSUR_CHOR

    async def select_chor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        chor = int(query.data.split("_")[2])
        context.user_data['selected_chor'] = chor

        await self._show_result(query, context)
        return ConversationHandler.END

    async def _show_result(self, query, context: ContextTypes.DEFAULT_TYPE):
        brand = context.user_data.get('selected_brand', '')
        model = context.user_data.get('selected_model', '')
        chor = context.user_data.get('selected_chor', 0)

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT laenge_mm, kern_mm, erste_wicklung_mm, zweite_wicklung_mm, typ, year, saiten_im_chor
                   FROM scales
                   WHERE brand = ? AND model = ? AND chor_nummer = ?""",
                (brand, model, chor)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                laenge, kern, w1, w2, typ, year, saiten = result

                text = f"📏 **{brand} — {model}**\n"
                text += f"🎵 Хор №{chor}\n\n"

                if laenge:
                    text += f"📐 Длина: {laenge} мм\n"
                if kern:
                    text += f"⭕ Керн: {kern} мм\n"
                if w1:
                    text += f"🟡 1-я обмотка: {w1} мм\n"
                if w2:
                    text += f"🟠 2-я обмотка: {w2} мм\n"
                if saiten:
                    text += f"🔢 Струн в хоре: {saiten}\n"
                if typ:
                    text += f"📋 Тип: {typ}\n"
                if year:
                    text += f"📅 Год: {year}\n"

                logger.info(f"✅ Мензура: {brand} {model} хор{chor}")
            else:
                text = f"❗ Данные для {brand} {model} хор {chor} не найдены."
                logger.warning(f"⚠️ Мензура не найдена: {brand} {model} хор{chor}")

            rows = [
                [InlineKeyboardButton("🔄 Новый поиск", callback_data="mensur_start")],
            ]
            rows.extend(get_nav_rows(include_back=False))

            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

        except Exception as e:
            logger.error(f"❌ Ошибка показа мензуры: {e}", exc_info=True)
            await query.edit_message_text(f"Ошибка: {e}")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Отменено.")
        context.user_data.clear()
        return ConversationHandler.END

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.start(update, context)
