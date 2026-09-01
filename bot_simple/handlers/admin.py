from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, ConversationHandler, MessageHandler,
    filters, CallbackQueryHandler
)
from handlers.base import BaseHandler
from services.admin_service import AdminService
from services.user_management_service import UserManagementService
from services.access_service import AccessService
from services.user_service import UserService
from app.logger import setup_logger

logger = setup_logger("AdminHandler")

EDIT_NAME, EDIT_LASTNAME, EDIT_EMAIL, EDIT_PHONE, EDIT_CITY, SEARCH_STATE = range(6)
PER_PAGE = 10


class AdminHandler(BaseHandler):
    def __init__(self, admin_service, user_mgmt_service, access_service, user_service):
        self.admin_service = admin_service
        self.user_mgmt_service = user_mgmt_service
        self.access_service = access_service
        self.user_service = user_service

    def get_command(self) -> str:
        return "admin"

    # ── ГЛАВНАЯ КОМАНДА ──
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db_user = self.user_service.get_by_telegram_id(user.id)
        if not self.access_service.is_admin_panel_visible(db_user):
            if update.callback_query:
                await update.callback_query.answer("❌ У вас нет прав", show_alert=True)
            else:
                await update.message.reply_text("❌ У вас нет прав.")
            return
        await self._send_admin_menu(update, context, db_user)

    # ── МЕНЮ АДМИНКИ ──
    async def _send_admin_menu(self, update, context, db_user):
        stats = self.admin_service.get_statistics()
        total_u = stats.get('total_users', 0)
        pending_u = stats.get('pending_users', 0)
        approved_u = stats.get('approved_users', 0)
        calcs = stats.get('calculations', 0)
        text = (
            "**👑 Панель управления**\n\n"
            "📊 **Статистика:**\n"
            f"• Всего пользователей: `{total_u}`\n"
            f"• Ожидают одобрения: `{pending_u}`\n"
            f"• Одобренных: `{approved_u}`\n"
            f"• Расчётов: `{calcs}`\n\n"
            "Выберите действие:"
        )
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="admin_refresh")],
            [InlineKeyboardButton("👥 Все пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("⏳ Заявки на доступ", callback_data="admin_pending")],
        ]
        if self.access_service.can_manage_admins(db_user):
            keyboard.append([InlineKeyboardButton("👑 Управление админами", callback_data="admin_admins")])
        keyboard.append([InlineKeyboardButton("🏠 В главное меню", callback_data="back_menu")])
        rm = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=rm, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=rm, parse_mode="Markdown")

    # ── СПИСОК ПОЛЬЗОВАТЕЛЕЙ ──
    async def show_users_list(self, update, context, page=0, search=None):
        query = update.callback_query
        users = self.user_mgmt_service.get_users_list(limit=PER_PAGE, offset=page * PER_PAGE, search=search)
        total = self.user_mgmt_service.get_users_count(search=search)
        total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

        if not users:
            msg = "📭 Список пуст"
            if search:
                msg = f"🔍 По запросу «{search}» ничего не найдено"
            kb = [[InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]]
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))
            return

        search_info = f" (поиск: «{search}»)" if search else ""
        text = f"**👥 Пользователи**{search_info}\nСтр. {page+1}/{total_pages} (всего: {total})\n\n"
        keyboard = []
        for u in users:
            st = "✅" if u["is_approved"] else "⏳"
            rl = "👑" if u["is_super_admin"] else ("⭐" if u["is_admin"] else "👤")
            city_p = f" | {u['city']}" if u["city"] else ""
            name_short = u["name"][:22]
            label = f"{st}{rl} {name_short}{city_p}"
            tid = u["telegram_id"]
            keyboard.append([InlineKeyboardButton(label, callback_data=f"user_detail_{tid}")])

        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("◀️ Назад", callback_data=f"users_page_{page-1}"))
        nav.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("Вперёд ▶️", callback_data=f"users_page_{page+1}"))
        keyboard.append(nav)
        keyboard.append([InlineKeyboardButton("🔍 Поиск", callback_data="admin_search_start")])
        keyboard.append([InlineKeyboardButton("◀️ Назад в админку", callback_data="admin_back")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # ── КАРТОЧКА ПОЛЬЗОВАТЕЛЯ ──
    async def show_user_detail(self, update, context):
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        await self._render_user_card(query, tid)

    async def _render_user_card(self, query, tid):
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        if not u:
            kb = [[InlineKeyboardButton("◀️ К списку", callback_data="admin_users")]]
            await query.edit_message_text("❌ Не найден", reply_markup=InlineKeyboardMarkup(kb))
            return

        status_t = "✅ Одобрен (доступ к клубу)" if u["is_approved"] else "⏳ Не одобрен"
        if u["is_super_admin"]:
            role_t = "👑 Супер-администратор"
        elif u["is_admin"]:
            role_t = "⭐ Администратор"
        else:
            role_t = "👤 Участник клуба"

        full_name = u["name"]
        if u["last_name"]:
            full_name += " " + u["last_name"]

        em = u["email"] or "—"
        ph = u["phone"] or "—"
        ci = u["city"] or "—"
        tg = u["telegram_id"]
        cr = u["created_at"]

        text = (
            "**✏️ Карточка пользователя**\n\n"
            f"👤 **Имя:** `{full_name}`\n"
            f"📧 **Email:** `{em}`\n"
            f"📱 **Телефон:** `{ph}`\n"
            f"🏙 **Город:** `{ci}`\n"
            f"🆔 **TG ID:** `{tg}`\n"
            f"📅 **Регистрация:** `{cr}`\n\n"
            f"**Статус:** {status_t}\n"
            f"**Роль:** {role_t}"
        )

        approve_label = "✅ Одобрен — нажать для смены" if u["is_approved"] else "⏳ Не одобрен — нажать для смены"

        keyboard = [
            [InlineKeyboardButton("✏️ Имя", callback_data=f"edit_name_{tid}"),
             InlineKeyboardButton("✏️ Фамилия", callback_data=f"edit_lastname_{tid}")],
            [InlineKeyboardButton("✏️ Email", callback_data=f"edit_email_{tid}"),
             InlineKeyboardButton("✏️ Телефон", callback_data=f"edit_phone_{tid}")],
            [InlineKeyboardButton("✏️ Город", callback_data=f"edit_city_{tid}")],
            [InlineKeyboardButton(approve_label, callback_data=f"toggle_approve_{tid}")],
            [InlineKeyboardButton("🗑️ Удалить пользователя", callback_data=f"confirm_delete_{tid}")],
            [InlineKeyboardButton("◀️ К списку пользователей", callback_data="admin_users")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # ── ПЕРЕКЛЮЧЕНИЕ ОДОБРЕНИЯ ──
    async def toggle_user_approval(self, update, context):
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        result = self.user_mgmt_service.toggle_approve(tid)
        if result is not None:
            s = "✅ одобрен" if result else "⏳ не одобрен"
            await query.answer(f"Статус: {s}")
            await self._render_user_card(query, tid)
        else:
            await query.answer("❌ Ошибка", show_alert=True)

    # ── УДАЛЕНИЕ ──
    async def confirm_delete(self, update, context):
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        if not u:
            await query.edit_message_text("❌ Не найден")
            return
        nm = u["name"]
        text = (
            f"⚠️ **Вы уверены?**\n\n"
            f"Удалить **{nm}** (`{tid}`)?\n\n"
            f"Все данные и расчёты будут удалены.\n"
            f"Это **необратимо**!"
        )
        kb = [
            [InlineKeyboardButton("🗑️ Да, удалить", callback_data=f"do_delete_{tid}"),
             InlineKeyboardButton("❌ Отмена", callback_data=f"user_detail_{tid}")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    async def do_delete(self, update, context):
        query = update.callback_query
        tid = int(query.data.split("_")[2])
        if self.user_mgmt_service.delete_user(tid):
            await query.answer("🗑️ Удалён")
            await self.show_users_list(update, context)
        else:
            await query.answer("❌ Ошибка", show_alert=True)

    # ── РЕДАКТИРОВАНИЕ ПОЛЕЙ ──
    async def _start_edit(self, query, tid, field_label, current_val, state):
        cur = current_val if current_val else "не указан"
        await query.edit_message_text(
            f"Текущее: **{cur}**\n\nВведите новое значение:",
            parse_mode="Markdown"
        )
        return state

    async def start_edit_name(self, update, context):
        q = update.callback_query; tid = int(q.data.split("_")[2])
        context.user_data["edit_tid"] = tid
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        return await self._start_edit(q, tid, "имя", u["name"] if u else "", EDIT_NAME)

    async def start_edit_lastname(self, update, context):
        q = update.callback_query; tid = int(q.data.split("_")[2])
        context.user_data["edit_tid"] = tid
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        return await self._start_edit(q, tid, "фамилию", u["last_name"] if u else "", EDIT_LASTNAME)

    async def start_edit_email(self, update, context):
        q = update.callback_query; tid = int(q.data.split("_")[2])
        context.user_data["edit_tid"] = tid
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        return await self._start_edit(q, tid, "email", u["email"] if u else "", EDIT_EMAIL)

    async def start_edit_phone(self, update, context):
        q = update.callback_query; tid = int(q.data.split("_")[2])
        context.user_data["edit_tid"] = tid
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        return await self._start_edit(q, tid, "телефон", u["phone"] if u else "", EDIT_PHONE)

    async def start_edit_city(self, update, context):
        q = update.callback_query; tid = int(q.data.split("_")[2])
        context.user_data["edit_tid"] = tid
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        return await self._start_edit(q, tid, "город", u["city"] if u else "", EDIT_CITY)

    async def _process_edit(self, update, context, field, label):
        tid = context.user_data.get("edit_tid")
        val = update.message.text.strip()
        if tid and self.user_mgmt_service.update_user(tid, field, val):
            await update.message.reply_text(f"✅ {label} обновлён: {val}")
            await self._send_card_message(update, tid)
        else:
            await update.message.reply_text("❌ Ошибка обновления")
        context.user_data.clear()
        return ConversationHandler.END

    async def process_edit_name(self, update, context):
        return await self._process_edit(update, context, "first_name", "Имя")

    async def process_edit_lastname(self, update, context):
        return await self._process_edit(update, context, "last_name", "Фамилия")

    async def process_edit_email(self, update, context):
        return await self._process_edit(update, context, "email", "Email")

    async def process_edit_phone(self, update, context):
        return await self._process_edit(update, context, "phone", "Телефон")

    async def process_edit_city(self, update, context):
        return await self._process_edit(update, context, "city", "Город")

    async def cancel_edit(self, update, context):
        tid = context.user_data.get("edit_tid")
        context.user_data.clear()
        if tid:
            await self._send_card_message(update, tid)
        else:
            await update.message.reply_text("Отменено.")
        return ConversationHandler.END

    async def _send_card_message(self, update, tid):
        u = self.user_mgmt_service.get_user_by_telegram_id(tid)
        if not u:
            await update.message.reply_text("❌ Не найден")
            return
        full_name = u["name"]
        if u["last_name"]:
            full_name += " " + u["last_name"]
        em = u["email"] or "—"
        ph = u["phone"] or "—"
        ci = u["city"] or "—"
        st = "✅ Одобрен" if u["is_approved"] else "⏳ Не одобрен"
        approve_lbl = "✅ Одобрен — сменить" if u["is_approved"] else "⏳ Не одобрен — сменить"
        text = (
            "**✏️ Карточка обновлена**\n\n"
            f"👤 **Имя:** `{full_name}`\n"
            f"📧 **Email:** `{em}`\n"
            f"📱 **Телефон:** `{ph}`\n"
            f"🏙 **Город:** `{ci}`\n"
            f"🆔 **TG ID:** `{u['telegram_id']}`\n"
            f"📅 **Регистрация:** `{u['created_at']}`\n\n"
            f"**Статус:** {st}"
        )
        kb = [
            [InlineKeyboardButton("✏️ Имя", callback_data=f"edit_name_{tid}"),
             InlineKeyboardButton("✏️ Фамилия", callback_data=f"edit_lastname_{tid}")],
            [InlineKeyboardButton("✏️ Email", callback_data=f"edit_email_{tid}"),
             InlineKeyboardButton("✏️ Телефон", callback_data=f"edit_phone_{tid}")],
            [InlineKeyboardButton("✏️ Город", callback_data=f"edit_city_{tid}")],
            [InlineKeyboardButton(approve_lbl, callback_data=f"toggle_approve_{tid}")],
            [InlineKeyboardButton("🗑️ Удалить", callback_data=f"confirm_delete_{tid}")],
            [InlineKeyboardButton("◀️ К списку", callback_data="admin_users")],
        ]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # ── ПОИСК ──
    async def start_search(self, update, context):
        q = update.callback_query
        await q.edit_message_text(
            "🔍 **Поиск пользователей**\n\n"
            "Введите имя, email, телефон или город:\n"
            "(или /cancel для отмены)",
            parse_mode="Markdown"
        )
        return SEARCH_STATE

    async def process_search(self, update, context):
        term = update.message.text.strip()
        users = self.user_mgmt_service.get_users_list(limit=PER_PAGE, offset=0, search=term)
        total = self.user_mgmt_service.get_users_count(search=term)
        if not users:
            await update.message.reply_text(
                f"📭 По запросу «{term}» ничего не найдено.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]])
            )
        else:
            tp = max(1, (total + PER_PAGE - 1) // PER_PAGE)
            text = f"**🔍 Результаты:** «{term}»\nНайдено: {total} (стр. 1/{tp})\n\n"
            kb = []
            for u in users:
                st = "✅" if u["is_approved"] else "⏳"
                rl = "👑" if u["is_super_admin"] else ("⭐" if u["is_admin"] else "👤")
                cp = f" | {u['city']}" if u["city"] else ""
                nm = u["name"][:22]
                kb.append([InlineKeyboardButton(f"{st}{rl} {nm}{cp}", callback_data=f"user_detail_{u['telegram_id']}")])
            kb.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        context.user_data.clear()
        return ConversationHandler.END

    # ── ЗАЯВКИ ──
    async def show_pending_users(self, update, context):
        users = self.user_mgmt_service.get_pending_users()
        if not users:
            kb = [[InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]]
            await update.callback_query.edit_message_text("✅ Нет ожидающих заявок", reply_markup=InlineKeyboardMarkup(kb))
            return
        text = "**⏳ Заявки на доступ:**\n\n"
        kb = []
        for u in users:
            info = u["name"]
            if u["city"]:
                info += f" | {u['city']}"
            cr = u["created_at"]
            tg = u["telegram_id"]
            text += f"⏳ `{tg}` — {info} ({cr})\n"
            kb.append([
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{tg}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{tg}"),
            ])
        kb.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
        await update.callback_query.edit_message_text(
            text + "\n*Нажмите кнопку*",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown"
        )

    # ── УПРАВЛЕНИЕ АДМИНАМИ ──
    async def show_admins_management(self, update, context):
        users = self.user_mgmt_service.get_users_list(limit=50)
        admins = [u for u in users if u["is_admin"] or u["is_super_admin"]]
        if not admins:
            kb = [[InlineKeyboardButton("◀️ Назад", callback_data="admin_back")]]
            await update.callback_query.edit_message_text("📭 Нет администраторов", reply_markup=InlineKeyboardMarkup(kb))
            return
        text = "**👑 Управление администраторами**\n\n"
        kb = []
        my_id = update.effective_user.id
        for u in admins:
            icon = "👑" if u["is_super_admin"] else "⭐"
            tg = u["telegram_id"]
            nm = u["name"]
            text += f"{icon} `{tg}` — {nm}\n"
            row = []
            if tg != my_id:
                sa_lbl = "👑 Супер-админ" if u["is_super_admin"] else "➕ Супер-админ"
                ad_lbl = "⭐ Админ" if u["is_admin"] else "➖ Админ"
                row.append(InlineKeyboardButton(sa_lbl, callback_data=f"toggle_super_{tg}"))
                row.append(InlineKeyboardButton(ad_lbl, callback_data=f"toggle_admin_{tg}"))
            if row:
                kb.append(row)
        kb.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
        await update.callback_query.edit_message_text(
            text + "\n*⚠️ Свои права изменить нельзя*",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown"
        )

    # ── НАЗАД В АДМИНКУ ──
    async def back_to_admin(self, update, context):
        q = update.callback_query
        await q.answer()
        db_user = self.user_service.get_by_telegram_id(update.effective_user.id)
        if db_user:
            await self._send_admin_menu(update, context, db_user)
        else:
            await q.edit_message_text("❌ Ошибка")

    # ── ConversationHandler ──
    def get_edit_conversation_handler(self):
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start_edit_name, pattern=r"^edit_name_\d+$"),
                CallbackQueryHandler(self.start_edit_lastname, pattern=r"^edit_lastname_\d+$"),
                CallbackQueryHandler(self.start_edit_email, pattern=r"^edit_email_\d+$"),
                CallbackQueryHandler(self.start_edit_phone, pattern=r"^edit_phone_\d+$"),
                CallbackQueryHandler(self.start_edit_city, pattern=r"^edit_city_\d+$"),
                CallbackQueryHandler(self.start_search, pattern=r"^admin_search_start$"),
            ],
            states={
                EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_name)],
                EDIT_LASTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_lastname)],
                EDIT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_email)],
                EDIT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_phone)],
                EDIT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_edit_city)],
                SEARCH_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_search)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_edit)],
            name="admin_edit_conv",
        )