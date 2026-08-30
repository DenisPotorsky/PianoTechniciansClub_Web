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

logger = setup_logger("AgeHandler")

AGE_TYPE, AGE_BRAND, AGE_SERIAL = range(3)


def normalize(text: str) -> str:
    """Транслитерирует умляуты и приводит к нижнему регистру"""
    if not text:
        return ""
    return unidecode(text).lower().strip()


class AgeHandler(BaseHandler):
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.db_path = config.AGE_DB_PATH

    def get_command(self) -> str:
        return "age"

    def get_conversation_handler(self):
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start, pattern="^age_start$"),
                CommandHandler("age", self.start)
            ],
            states={
                AGE_TYPE: [CallbackQueryHandler(self.select_type, pattern="^age_type_")],
                AGE_BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_brand)],
                AGE_SERIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_serial)],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                CallbackQueryHandler(self.nav_to_main_menu, pattern="^back_menu$"),
                CallbackQueryHandler(self.nav_back_to_start, pattern="^age_start$"),
            ],
            name="age_conv"
        )

    async def nav_back_to_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        await self.start(update, context)
        return AGE_TYPE

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
            [InlineKeyboardButton("🌐 Сайт клуба", url="https://piano-technicians.club")],
            [
                InlineKeyboardButton("📢 Канал", url=cfg.CHANNEL_URL),
                InlineKeyboardButton("💬 Чат", url=cfg.CHAT_URL)
            ]
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
            raise FileNotFoundError(f"База брендов не найдена: {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        # Регистрируем функцию normalize в SQLite для использования в запросах
        conn.create_function("normalize", 1, lambda x: normalize(x))
        # Включаем регистронезависимый LIKE
        conn.execute("PRAGMA case_sensitive_like = OFF")
        return conn

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        rows = [
            [InlineKeyboardButton("🇪🇺 Иностранные", callback_data="age_type_foreign")],
            [InlineKeyboardButton("🇷🇺 Отечественные", callback_data="age_type_russian")],
        ]
        rows.extend(get_nav_rows(include_back=False))
        keyboard = InlineKeyboardMarkup(rows)

        text = "📅 **Определение возраста фортепиано**\n\nВыберите тип бренда:"

        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return AGE_TYPE

    async def select_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        b_type = query.data.split("_")[2]
        context.user_data['brand_type'] = b_type
        rows = get_nav_rows(back_callback="age_start")
        await query.edit_message_text(
            f"Введите название бренда ({'иностранный' if b_type == 'foreign' else 'отечественный'}):",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        return AGE_BRAND

    async def input_brand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raw_input = update.message.text.strip()
        search_term = normalize(raw_input)
        brand_type = context.user_data.get('brand_type', 'foreign')
        context.user_data['brand_name_raw'] = raw_input

        logger.info(f"🔍 Поиск бренда: '{raw_input}' → '{search_term}' (тип: {brand_type})")

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            results = []

            # Стратегия 1: нормализованное сравнение с фильтром по типу
            # Находит: Förster=forster, Blüthner=bluthner, Bösendorfer=bosendorfer
            cursor.execute(
                """SELECT id, name, country, info FROM brands 
                   WHERE type = ? AND normalize(name) LIKE ?""",
                (brand_type, f"%{search_term}%")
            )
            results = cursor.fetchall()
            strategy = "normalize+type"

            # Стратегия 2: обычное NOCASE сравнение с фильтром по типу
            if not results:
                cursor.execute(
                    """SELECT id, name, country, info FROM brands 
                       WHERE type = ? AND name LIKE ? COLLATE NOCASE""",
                    (brand_type, f"%{raw_input}%")
                )
                results = cursor.fetchall()
                strategy = "nocase+type"

            # Стратегия 3: нормализованное сравнение БЕЗ фильтра по типу
            # На случай если пользователь выбрал не тот тип
            if not results:
                cursor.execute(
                    """SELECT id, name, country, info, type FROM brands 
                       WHERE normalize(name) LIKE ?""",
                    (f"%{search_term}%",)
                )
                cross_results = cursor.fetchall()
                if cross_results:
                    results = [(r[0], r[1], r[2], r[3]) for r in cross_results]
                    strategy = "normalize+cross_type"
                    logger.info(f"💡 Бренд найден в другом типе: {results[0][1]}")

            # Стратегия 4: NOCASE без фильтра по типу (последний шанс)
            if not results:
                cursor.execute(
                    """SELECT id, name, country, info FROM brands 
                       WHERE name LIKE ? COLLATE NOCASE""",
                    (f"%{raw_input}%",)
                )
                results = cursor.fetchall()
                strategy = "nocase+cross_type"

            conn.close()

            logger.info(f"📊 Результаты поиска: {len(results)} (стратегия: {strategy})")

            if not results:
                rows = get_nav_rows(back_callback="age_start")
                await update.message.reply_text(
                    f"❗ Бренд «{raw_input}» не найден.\nПроверьте написание и попробуйте снова.",
                    reply_markup=InlineKeyboardMarkup(rows)
                )
                return AGE_BRAND

            if len(results) == 1:
                brand_id, name, country, info = results[0]
                context.user_data['brand_id'] = brand_id
                context.user_data['brand_display'] = name

                brand_info = f"**{name}**\n📍 {country}"
                if info:
                    brand_info += f"\nℹ️ {info}"

                rows = get_nav_rows(back_callback="age_start")
                await update.message.reply_text(
                    f"{brand_info}\n\nВведите серийный номер:",
                    reply_markup=InlineKeyboardMarkup(rows),
                    parse_mode="Markdown"
                )
                return AGE_SERIAL
            else:
                text = "Найдено несколько брендов:\n\n"
                for i, (_, name, country, _) in enumerate(results[:10], 1):
                    text += f"{i}. **{name}** ({country})\n"
                text += "\nВведите точное название бренда:"

                rows = get_nav_rows(back_callback="age_start")
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
                return AGE_BRAND

        except Exception as e:
            logger.error(f"❌ Ошибка поиска бренда: {e}", exc_info=True)
            rows = get_nav_rows(back_callback="age_start")
            await update.message.reply_text(f"Ошибка базы данных: {e}", reply_markup=InlineKeyboardMarkup(rows))
            return ConversationHandler.END

    async def input_serial(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        serial_text = update.message.text.strip().replace(" ", "").replace("#", "")
        brand_id = context.user_data.get('brand_id')
        brand_name = context.user_data.get('brand_display', 'Неизвестный')

        try:
            serial = int(serial_text)
        except ValueError:
            rows = get_nav_rows(back_callback="age_start")
            await update.message.reply_text(
                "❗ Серийный номер должен содержать только цифры.",
                reply_markup=InlineKeyboardMarkup(rows)
            )
            return AGE_SERIAL

        logger.info(f"📅 Поиск года: бренд={brand_name} (ID:{brand_id}), серийный={serial}")

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT year, model, info, serial_start, serial_end 
                   FROM serial_ranges 
                   WHERE brand_id = ? AND serial_start <= ? AND serial_end >= ?""",
                (brand_id, serial, serial)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                year, model, info, s_start, s_end = result

                text = f"🎹 **{brand_name}**\n\n"
                text += f"📅 **Год выпуска: {year}**\n"
                text += f"🔢 Серийный: {serial} (диапазон {s_start}–{s_end})\n"
                if model:
                    text += f"📋 Модель: {model}\n"
                if info:
                    text += f"ℹ️ {info}\n"

                logger.info(f"✅ Найден год: {year} для {brand_name} #{serial}")
            else:
                text = f"🎹 **{brand_name}**\n\n"
                text += f"❗ Серийный номер **{serial}** не найден в базе.\n\n"
                text += "Возможные причины:\n"
                text += "• Номер указан неверно\n"
                text += "• Инструмент выпущен до начала ведения записей\n"
                text += "• Бренд имеет нестандартную нумерацию\n\n"
                text += "Попробуйте проверить номер на раме инструмента."

                logger.warning(f"⚠️ Год не найден для {brand_name} #{serial}")

            rows = [
                [InlineKeyboardButton("🔄 Новый поиск", callback_data="age_start")],
            ]
            rows.extend(get_nav_rows(include_back=False))
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
            context.user_data.clear()
            return ConversationHandler.END

        except Exception as e:
            logger.error(f"❌ Ошибка поиска года: {e}", exc_info=True)
            rows = get_nav_rows(back_callback="age_start")
            await update.message.reply_text(f"Ошибка поиска: {e}", reply_markup=InlineKeyboardMarkup(rows))
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Отменено.")
        context.user_data.clear()
        return ConversationHandler.END

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.start(update, context)