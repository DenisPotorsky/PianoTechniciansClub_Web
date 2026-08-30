from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, \
    CallbackQueryHandler
from handlers.base import BaseHandler
from services.admin_service import AdminService
from services.user_management_service import UserManagementService
from services.access_service import AccessService
from services.user_service import UserService
from app.logger import setup_logger

logger = setup_logger("AdminHandler")

EDIT_NAME, EDIT_EMAIL = range(2)


class AdminHandler(BaseHandler):
    def __init__(self, admin_service: AdminService, user_mgmt_service: UserManagementService,
                 access_service: AccessService, user_service: UserService):
        self.admin_service = admin_service
        self.user_mgmt_service = user_mgmt_service
        self.access_service = access_service
        self.user_service = user_service

    def get_command(self) -> str:
        return "admin"

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)

        if not self.access_service.is_admin_panel_visible(db_user):
            if update.callback_query:
                await update.callback_query.answer("❌ У вас нет прав", show_alert=True)
            else:
                await update.message.reply_text("❌ У вас нет прав для доступа к панели управления.")
            return

        await self._send_admin_menu(update, context, db_user)

    async def _send_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, db_user):
        stats = self.admin_service.get_statistics()
        text = (
            f"**Панель управления**\n\n"
            f"📊 **Статистика:**\n"
            f"• Всего пользователей: `{stats.get('total_users', 0)}`\n"
            f"• Ожидают одобрения: `{stats.get('pending_users', 0)}`\n"
            f"• Одобренных: `{stats.get('approved_users', 0)}`\n"
            f"• Расчётов: `{stats.get('calculations', 0)}`\n\n"
            f"Выберите действие:"
        )
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_refresh")],
            [InlineKeyboardButton("⏳ Заявки на доступ", callback_data="admin_pending")],
            [InlineKeyboardButton("👥 Все пользователи", callback_data="admin_users")]
        ]
        if self.access_service.can_manage_admins(db_user):
            keyboard.append([InlineKeyboardButton("👑 Управление админами", callback_data="admin_admins")])
        keyboard.append([InlineKeyboardButton("🏠 В главное меню", callback_data="back_menu")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка отправки меню: {e}")

    async def show_users_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users = self.user_mgmt_service.get_users_list(limit=20)
        if not users:
            await update.callback_query.edit_message_text("📭 Список пользователей пуст")
            return

        text = "**Все пользователи:**\n\n"
        keyboard = []
        for u in users:
            status_icon = "✅" if u["is_approved"] else "⏳"
            admin_icon = "👑" if u["is_admin"] else ""
            text += f"{status_icon} {admin_icon} `{u['telegram_id']}` — {u['name']}\n"
            keyboard.append([InlineKeyboardButton(
                f"{'✅' if u['is_approved'] else '⏳'} {u['name'][:25]}",
                callback_data=f"user_detail_{u['telegram_id']}"
            )])

        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
        await update.callback_query.edit_message_text(
            text + "\n*Нажмите на пользователя для деталей*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    async def show_user_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Экран детального просмотра пользователя"""
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)

        if not u:
            await query.edit_message_text("❌ Пользователь не найден")
            return

        text = (
            f"**Карточка пользователя**\n\n"
            f"👤 Имя: `{u['name']}`\n"
            f"📧 Email: `{u['email'] or 'не указан'}`\n"
            f"🆔 Telegram ID: `{u['telegram_id']}`\n"
            f"✅ Одобрен: {'Да' if u['is_approved'] else 'Нет'}\n"
            f"👑 Админ: {'Да' if u['is_admin'] else 'Нет'}\n"
            f" Супер-админ: {'Да' if u['is_super_admin'] else 'Нет'}"
        )

        keyboard = [
            [InlineKeyboardButton("✏️ Изменить имя", callback_data=f"edit_name_{tid}")],
            [InlineKeyboardButton("✏️ Изменить email", callback_data=f"edit_email_{tid}")],
            [InlineKeyboardButton("🗑️ Удалить пользователя", callback_data=f"confirm_delete_{tid}")]
        ]
        keyboard.append([InlineKeyboardButton("◀️ К списку", callback_data="admin_users")])

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    async def confirm_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение удаления"""
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)

        if not u:
            await query.edit_message_text("❌ Пользователь не найден")
            return

        text = f"⚠️ **Вы уверены?**\n\nУдалить пользователя **{u['name']}** (`{tid}`)?\nЭто действие необратимо!"
        keyboard = [
            [
                InlineKeyboardButton("🗑️ Да, удалить", callback_data=f"do_delete_{tid}"),
                InlineKeyboardButton("❌ Отмена", callback_data=f"user_detail_{tid}")
            ]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    async def do_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        success = self.user_mgmt_service.delete_user(tid)
        if success:
            await query.answer("🗑️ Пользователь удалён")
            await self.show_users_list(update, context)
        else:
            await query.answer("❌ Ошибка удаления")

    async def start_edit_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        context.user_data['edit_tid'] = tid
        await query.edit_message_text(f"Введите новое имя для пользователя `{tid}`:")
        return EDIT_NAME

    async def process_edit_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tid = context.user_data.get('edit_tid')
        new_name = update.message.text.strip()
        if tid and self.user_mgmt_service.update_user(tid, "first_name", new_name):
            await update.message.reply_text(f"✅ Имя обновлено на: {new_name}")
        else:
            await update.message.reply_text("❌ Ошибка обновления")
        context.user_data.clear()
        return ConversationHandler.END

    async def start_edit_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        context.user_data['edit_tid'] = tid
        await query.edit_message_text(f"Введите новый email для пользователя `{tid}`:")
        return EDIT_EMAIL

    async def process_edit_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tid = context.user_data.get('edit_tid')
        new_email = update.message.text.strip()
        if tid and self.user_mgmt_service.update_user(tid, "email", new_email):
            await update.message.reply_text(f"✅ Email обновлён на: {new_email}")
        else:
            await update.message.reply_text("❌ Ошибка обновления")
        context.user_data.clear()
        return ConversationHandler.END

    async def cancel_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Отменено.")
        context.user_data.clear()
        return ConversationHandler.END

    def get_edit_conversation_handler(self):
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start_edit_name, pattern=r"^edit_name_\d+$"),
                CallbackQueryHandler(self.start_edit_email, pattern=r"^edit_email_\d+$"),
            ],
            states={
                EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_name)],
                EDIT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_email)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_edit)],
            name="admin_edit_conv"
        )

    async def show_pending_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users = self.user_mgmt_service.get_pending_users()
        if not users:
            await update.callback_query.edit_message_text("✅ Нет ожидающих заявок")
            return

        text = "**Заявки на доступ:**\n\n"
        keyboard = []
        for u in users:
            text += f"⏳ `{u['telegram_id']}` — {u['name']}\n"
            keyboard.append([
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{u['telegram_id']}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{u['telegram_id']}")
            ])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
        await update.callback_query.edit_message_text(
            text + "\n*Нажмите кнопку для действия*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    async def show_admins_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users = self.user_mgmt_service.get_users_list(limit=50)
        admins = [u for u in users if u["is_admin"] or u["is_super_admin"]]
        if not admins:
            await update.callback_query.edit_message_text("📭 Нет администраторов")
            return

        text = "**Управление администраторами**\n\n"
        keyboard = []
        for u in admins:
            super_icon = "" if u["is_super_admin"] else "️"
            text += f"{super_icon} `{u['telegram_id']}` — {u['name']}\n"
            row = []
            if u["telegram_id"] != update.effective_user.id:
                row.append(InlineKeyboardButton(
                    f"{'✅' if u['is_super_admin'] else '➕'} Супер-админ",
                    callback_data=f"toggle_super_{u['telegram_id']}"
                ))
                row.append(InlineKeyboardButton(
                    f"{'🔒' if u['is_admin'] else '➖'} Админ",
                    callback_data=f"toggle_admin_{u['telegram_id']}"
                ))
            if row:
                keyboard.append(row)
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
        await update.callback_query.edit_message_text(
            text + "\n*⚠️ Вы не можете изменить свои права*",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    async def back_to_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db_user = self.user_service.get_by_telegram_id(update.effective_user.id)
        if db_user:
            await self._send_admin_menu(update, context, db_user)
        else:
            await query.edit_message_text("❌ Ошибка")