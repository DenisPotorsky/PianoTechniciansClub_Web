from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    MessageHandler, filters, CommandHandler
)
from handlers.base import BaseHandler
from handlers.start import get_nav_rows
from services.calculator import StringCalculator
from services.user_service import UserService
from services.access_service import AccessService
from app.database import SessionLocal
from models.db_models import Calculation
from app.logger import setup_logger

logger = setup_logger("CalculatorHandler")

CALC_WINDING, CALC_RATIO, CALC_CORE, CALC_TOTAL, CALC_LEN = range(5)


class CalculatorHandler(BaseHandler):
    def __init__(self, user_service: UserService, access_service: AccessService):
        self.user_service = user_service
        self.access_service = access_service
        self.calculator = StringCalculator()

    def get_command(self) -> str:
        return "calc"

    def get_conversation_handler(self):
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start, pattern="^calc_start$"),
                CommandHandler("calc", self.start)
            ],
            states={
                CALC_WINDING: [CallbackQueryHandler(self.select_winding, pattern="^type_")],
                CALC_RATIO: [CallbackQueryHandler(self.select_ratio, pattern="^ratio_")],
                CALC_CORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_core)],
                CALC_TOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_total)],
                CALC_LEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_length)],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                # Навигация внутри ConversationHandler
                CallbackQueryHandler(self.nav_back_to_start, pattern="^calc_start$"),
                CallbackQueryHandler(self.nav_to_main_menu, pattern="^back_menu$"),
            ],
            name="calculator_conv"
        )

    async def nav_back_to_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Назад к началу калькулятора"""
        context.user_data.clear()
        await self.start(update, context)
        return CALC_WINDING

    async def nav_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выход в главное меню"""
        context.user_data.clear()
        query = update.callback_query
        if query:
            await query.answer()
        # Импортируем здесь, чтобы избежать циклического импорта
        from handlers.start import StartHandler
        # Просто отправляем главное меню через edit_message
        from app.config import config
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

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)
        if not db_user:
            db_user = self.user_service.get_or_create(user.id, user.username, user.first_name)

        context.user_data.clear()
        rows = [
            [InlineKeyboardButton("🔵 Одиночная", callback_data="type_single")],
            [InlineKeyboardButton("🔴 Двойная", callback_data="type_double")],
        ]
        rows.extend(get_nav_rows(include_back=False))
        keyboard = InlineKeyboardMarkup(rows)

        text = "🧮 **Калькулятор басовых струн**\n\nВыберите тип навивки:"

        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return CALC_WINDING

    async def select_winding(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        w_type = query.data.split("_")[1]
        context.user_data['winding_type'] = w_type

        if w_type == 'double':
            rows = [
                [InlineKeyboardButton("1 : 2", callback_data="ratio_2")],
                [InlineKeyboardButton("1 : 2.5", callback_data="ratio_2.5")],
                [InlineKeyboardButton("1 : 3", callback_data="ratio_3")],
            ]
            rows.extend(get_nav_rows(back_callback="calc_start"))
            await query.edit_message_text("Выберите соотношение:", reply_markup=InlineKeyboardMarkup(rows))
            return CALC_RATIO
        else:
            rows = get_nav_rows(back_callback="calc_start")
            await query.edit_message_text("Введите диаметр **КЕРНА** (мм):", reply_markup=InlineKeyboardMarkup(rows))
            return CALC_CORE

    async def select_ratio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        ratio = float(query.data.split("_")[1])
        context.user_data['ratio'] = ratio
        rows = get_nav_rows(back_callback="calc_start")
        await query.edit_message_text(
            f"Соотношение 1:{ratio}. Введите диаметр **КЕРНА** (мм):",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        return CALC_CORE

    async def input_core(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            val = float(update.message.text.replace(',', '.'))
            context.user_data['core'] = val
            rows = get_nav_rows(back_callback="calc_start")
            await update.message.reply_text(
                f"Керн: {val} мм. Введите **ОБЩИЙ** диаметр (мм):",
                reply_markup=InlineKeyboardMarkup(rows)
            )
            return CALC_TOTAL
        except ValueError:
            rows = get_nav_rows(back_callback="calc_start")
            await update.message.reply_text("❗ Введите число!", reply_markup=InlineKeyboardMarkup(rows))
            return CALC_CORE

    async def input_total(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            val = float(update.message.text.replace(',', '.'))
            core = context.user_data['core']
            if val <= core:
                rows = get_nav_rows(back_callback="calc_start")
                await update.message.reply_text("❗ Общий должен быть больше керна!",
                                                reply_markup=InlineKeyboardMarkup(rows))
                return CALC_TOTAL
            context.user_data['total'] = val
            rows = get_nav_rows(back_callback="calc_start")
            await update.message.reply_text(
                f"Общий: {val} мм. Введите **ДЛИНУ** обмотки (мм):",
                reply_markup=InlineKeyboardMarkup(rows)
            )
            return CALC_LEN
        except ValueError:
            rows = get_nav_rows(back_callback="calc_start")
            await update.message.reply_text("❗ Введите число!", reply_markup=InlineKeyboardMarkup(rows))
            return CALC_TOTAL

    async def input_length(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            length = float(update.message.text.replace(',', '.'))
            data = context.user_data

            result = self.calculator.calculate(
                winding_type=data['winding_type'], core=data['core'],
                total=data['total'], length=length, ratio=data.get('ratio', 2.5)
            )

            db = SessionLocal()
            try:
                user = self.user_service.get_by_telegram_id(update.effective_user.id)
                calc = Calculation(
                    user_id=user.id, winding_type=data['winding_type'],
                    core_diameter=data['core'], total_diameter=data['total'],
                    string_length=length, result_data=str(result)
                )
                db.add(calc)
                db.commit()
            finally:
                db.close()

            if data['winding_type'] == 'single':
                msg = (f"✅ **Результат**\n🟡 Медь: {result['d_cu']} мм\n"
                       f"🔄 Витков: {result['turns']}\n📏 Длина: {result['len_m']} м\n"
                       f"⚖️ Вес: {result['weight_g']} г")
            else:
                msg = (f"✅ **Результат (1:{result['ratio']})**\n"
                       f"🟡 Первичка: {result['d1']} мм ({result['l1_m']} м, {result['w1_g']} г)\n"
                       f"🟠 Вторичка: {result['d2']} мм ({result['l2_m']} м, {result['w2_g']} г)\n"
                       f"⚖️ Общий вес: {result['total_w']} г")

            rows = [
                [InlineKeyboardButton("🔄 Новый расчёт", callback_data="calc_start")],
            ]
            rows.extend(get_nav_rows(include_back=False))
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
            context.user_data.clear()
            return ConversationHandler.END

        except Exception as e:
            logger.error(f"❌ Ошибка расчёта: {e}", exc_info=True)
            rows = get_nav_rows(back_callback="calc_start")
            await update.message.reply_text(f"Ошибка: {e}", reply_markup=InlineKeyboardMarkup(rows))
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Отменено.")
        context.user_data.clear()
        return ConversationHandler.END

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.start(update, context)
