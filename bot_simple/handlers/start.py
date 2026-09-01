from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from services.user_service import UserService
from services.access_service import AccessService
from services.notification_service import NotificationService
from services.user_management_service import UserManagementService
from app.config import config
from app.logger import setup_logger

logger = setup_logger("StartHandler")


def get_nav_rows(include_back: bool = True, back_callback: str = "back_menu") -> list[list[InlineKeyboardButton]]:
    """Возвращает строки навигации"""
    row = []
    if include_back:
        row.append(InlineKeyboardButton("◀️ Назад", callback_data=back_callback))
    row.append(InlineKeyboardButton("🏠 Главная", callback_data="back_menu"))
    return [row]


class StartHandler(BaseHandler):
    def __init__(self, user_service: UserService, access_service: AccessService,
                 notification_service: NotificationService, user_mgmt_service: UserManagementService):
        self.user_service = user_service
        self.access_service = access_service
        self.notification_service = notification_service
        self.user_mgmt_service = user_mgmt_service

    def get_command(self) -> str:
        return "start"

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)

        # === Сценарий 1: Пользователь уже есть в базе ===
        if db_user:
            has_access, reason = self.access_service.has_access(db_user)

            if reason == "pending_approval":
                await update.message.reply_text(
                    f"Привет, {user.first_name}! 👋\n\n"
                    f"⏳ Ваша заявка ожидает одобрения.\n"
                    f"Вы получите сообщение, когда администратор рассмотрит её."
                )
                return

            # Доступ разрешён — показываем полное главное меню
            await self._send_main_menu(update, db_user)
            return

        # === Сценарий 2: Новый пользователь — экран приветствия БЕЗ ссылок ===
        logger.info(f"👋 Новый посетитель: {user.first_name} ({user.id})")

        rows = [
            [InlineKeyboardButton("📝 Подать заявку на вступление", callback_data="apply_membership")],
        ]

        text = (
            f"Привет, {user.first_name}! 👋\n\n"
            f"**Piano Technicians Club** — это закрытый клуб для профессиональных фортепианных мастеров.\n\n"
            f"🔹 Калькулятор басовых струн\n"
            f"🔹 Атлас возрастов фортепиано\n"
            f"🔹 База мензур\n"
            f"🔹 Регулировочные параметры\n"
            f"🔹 Закрытое сообщество мастеров\n\n"
            f"Для доступа к инструментам и сообществу необходимо подать заявку."
        )

        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

    async def _send_main_menu(self, update: Update, db_user):
        """Главное меню ТОЛЬКО для одобренных пользователей"""
        rows = [
            [InlineKeyboardButton("🧮 Калькулятор струн", callback_data="calc_start")],
            [InlineKeyboardButton("📅 Возраст фортепиано", callback_data="age_start")],
            [InlineKeyboardButton("📏 Мензуры", callback_data="mensur_start")],
            [InlineKeyboardButton("🔧 Регулировка", callback_data="reg_start")],
            [InlineKeyboardButton("👤 Мой профиль", callback_data="profile_show")],
            [InlineKeyboardButton("🌐 Сайт клуба", url="https://piano-technicians.club")],
            [
                InlineKeyboardButton("📢 Канал", url=config.CHANNEL_URL),
                InlineKeyboardButton("💬 Чат", url=config.CHAT_URL)
            ]
        ]
        if self.access_service.is_admin_panel_visible(db_user):
            role_icon = "" if db_user.is_super_admin else "️"
            rows.append([InlineKeyboardButton(f"{role_icon} Панель управления", callback_data="admin_panel")])
        rows.append([InlineKeyboardButton("ℹ️ О клубе", callback_data="about")])

        status_text = "Супер-администратор" if db_user.is_super_admin else \
                      "Администратор" if db_user.is_admin else "Участник клуба"

        text = (
            f"Привет, {update.effective_user.first_name}! 👋\n\n"
            f"Добро пожаловать в **Piano Technicians Club**.\n"
            f"✅ Статус: {status_text}\n\n"
            f"Выберите инструмент:"
        )

        reply_markup = InlineKeyboardMarkup(rows)
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")