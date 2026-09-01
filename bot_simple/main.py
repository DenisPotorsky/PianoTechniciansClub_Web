from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from app.config import config
from app.database import SessionLocal
from repositories.user_repo import UserRepository
from repositories.subscription_repo import SubscriptionRepository
from services.user_service import UserService
from services.subscription_service import SubscriptionService
from services.access_service import AccessService
from services.admin_service import AdminService
from services.user_management_service import UserManagementService
from services.notification_service import NotificationService
from handlers.start import StartHandler
from handlers.calculator import CalculatorHandler
from handlers.age import AgeHandler
from handlers.mensur import MensurHandler
from handlers.regulating import RegulatingHandler
from handlers.admin import AdminHandler
from handlers.profile import ProfileHandler
from app.logger import setup_logger

logger = setup_logger("main")


class ScopedUserRepository:
    def get_by_telegram_id(self, tid):
        db = SessionLocal()
        try:
            return UserRepository(db).get_by_telegram_id(tid)
        finally:
            db.close()

    def create(self, data):
        db = SessionLocal()
        try:
            return UserRepository(db).create(data)
        finally:
            db.close()


class ScopedSubscriptionRepository:
    def get_by_user_id(self, uid):
        db = SessionLocal()
        try:
            return SubscriptionRepository(db).get_by_user_id(uid)
        finally:
            db.close()


def main():
    config.validate()

    user_repo = ScopedUserRepository()
    sub_repo = ScopedSubscriptionRepository()

    user_service = UserService(user_repo)
    sub_service = SubscriptionService(sub_repo)
    access_service = AccessService()
    admin_service = AdminService()
    user_mgmt_service = UserManagementService()

    application = Application.builder().token(config.BOT_TOKEN).build()
    notification_service = NotificationService(application.bot)

    start_handler = StartHandler(user_service, access_service, notification_service, user_mgmt_service)
    calc_handler = CalculatorHandler(user_service, access_service)
    age_handler = AgeHandler(user_service)
    mensur_handler = MensurHandler(user_service)
    regulating_handler = RegulatingHandler(user_service)
    profile_handler = ProfileHandler(user_service, access_service, notification_service, user_mgmt_service)
    admin_handler = AdminHandler(admin_service, user_mgmt_service, access_service, user_service)

    # ── КОМАНДЫ ──
    application.add_handler(CommandHandler("start", start_handler.handle))
    application.add_handler(CommandHandler("calc", calc_handler.handle))
    application.add_handler(CommandHandler("age", age_handler.handle))
    application.add_handler(CommandHandler("mensur", mensur_handler.handle))
    application.add_handler(CommandHandler("reg", regulating_handler.handle))
    application.add_handler(CommandHandler("profile", profile_handler.handle))
    application.add_handler(CommandHandler("admin", admin_handler.handle))

    # ── CONVERSATION HANDLERS ──
    application.add_handler(profile_handler.get_conversation_handler())
    application.add_handler(admin_handler.get_edit_conversation_handler())
    application.add_handler(calc_handler.get_conversation_handler())
    application.add_handler(age_handler.get_conversation_handler())
    application.add_handler(mensur_handler.get_conversation_handler())
    application.add_handler(regulating_handler.get_conversation_handler())

    # ── ГЛОБАЛЬНЫЙ CALLBACK ROUTER ──
    async def global_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query or not query.data:
            return

        data = query.data
        user = update.effective_user
        db_user = user_service.get_by_telegram_id(user.id)

        if data == "noop":
            await query.answer()
            return

        # ── НАВИГАЦИЯ ──
        if data == "back_menu":
            await query.answer()
            if db_user:
                has_access, _ = access_service.has_access(db_user)
                if has_access:
                    await start_handler._send_main_menu(update, db_user)
                else:
                    await query.edit_message_text("⏳ Ваша заявка ожидает одобрения.")
            else:
                await start_handler.handle(update, context)
            return

        # ── ЗАЯВКА НА ВСТУПЛЕНИЕ ──
        if data == "apply_membership":
            await query.answer()
            if not db_user:
                user_service.create_user(telegram_id=user.id, username=user.username, first_name=user.first_name)
            await query.edit_message_text(
                "📝 **Заявка отправлена!**\n\n"
                "Администратор рассмотрит вашу заявку.\n"
                "Вы получите уведомление о решении.\n\n"
                "Ожидайте ⏳",
                parse_mode="Markdown"
            )
            admin_ids = user_mgmt_service.get_admin_ids()
            if admin_ids:
                await notification_service.notify_admins_new_request(
                    user_name=user.first_name, telegram_id=user.id, admin_ids=admin_ids
                )
            return

        # ── ОДОБРЕНИЕ / ОТКЛОНЕНИЕ ──
        if data.startswith("approve_"):
            tid = int(data.split("_")[1])
            if user_mgmt_service.approve_user(tid):
                await query.answer("✅ Одобрен")
                await notification_service.notify_user_approved(tid)
                au = user_mgmt_service.get_user_by_telegram_id(tid)
                nm = au["name"] if au else str(tid)
                aids = user_mgmt_service.get_admin_ids()
                await notification_service.notify_admins_user_approved(
                    user_name=nm, telegram_id=tid, approved_by=user.first_name,
                    admin_ids=[a for a in aids if a != user.id]
                )
            else:
                await query.answer("❌ Ошибка", show_alert=True)
            return

        if data.startswith("reject_"):
            tid = int(data.split("_")[1])
            if user_mgmt_service.reject_user(tid):
                await query.answer("🚫 Отклонено")
                await notification_service.notify_user_rejected(tid)
            else:
                await query.answer("❌ Ошибка", show_alert=True)
            return

        # ── АДМИН-ПАНЕЛЬ ──
        if data == "admin_panel":
            await query.answer()
            await admin_handler.handle(update, context)
            return

        if data == "admin_refresh":
            await query.answer("🔄 Обновлено")
            await admin_handler.handle(update, context)
            return

        if data == "admin_back":
            await query.answer()
            await admin_handler.back_to_admin(update, context)
            return

        if data == "admin_users":
            await query.answer()
            await admin_handler.show_users_list(update, context, page=0)
            return

        if data.startswith("users_page_"):
            page = int(data.split("_")[2])
            await query.answer()
            await admin_handler.show_users_list(update, context, page=page)
            return

        if data == "admin_pending":
            await query.answer()
            await admin_handler.show_pending_users(update, context)
            return

        if data == "admin_admins":
            await query.answer()
            await admin_handler.show_admins_management(update, context)
            return

        # ── КАРТОЧКА ПОЛЬЗОВАТЕЛЯ ──
        if data.startswith("user_detail_"):
            await query.answer()
            await admin_handler.show_user_detail(update, context)
            return

        if data.startswith("toggle_approve_"):
            await admin_handler.toggle_user_approval(update, context)
            return

        if data.startswith("confirm_delete_"):
            await query.answer()
            await admin_handler.confirm_delete(update, context)
            return

        if data.startswith("do_delete_"):
            await admin_handler.do_delete(update, context)
            return

        # ── РОЛИ ──
        if data.startswith("toggle_admin_"):
            tid = int(data.split("_")[2])
            r = user_mgmt_service.toggle_admin(tid)
            if r is not None:
                s = "⭐ Админ" if r else "👤 Участник"
                await query.answer(f"Роль: {s}")
                await admin_handler.show_admins_management(update, context)
            else:
                await query.answer("❌ Ошибка", show_alert=True)
            return

        if data.startswith("toggle_super_"):
            tid = int(data.split("_")[2])
            r = user_mgmt_service.toggle_super_admin(tid)
            if r is not None:
                s = "👑 Супер-админ" if r else "⭐ Админ"
                await query.answer(f"Роль: {s}")
                await admin_handler.show_admins_management(update, context)
            else:
                await query.answer("❌ Ошибка", show_alert=True)
            return

        # ── ПРОФИЛЬ ──
        if data == "profile_show":
            await query.answer()
            await profile_handler.show_profile(update, context)
            return

        if data == "profile_logout":
            await profile_handler.logout_confirm(update, context)
            return

        if data == "profile_do_logout":
            await profile_handler.do_logout(update, context)
            return

        if data == "profile_delete_confirm":
            await profile_handler.delete_confirm(update, context)
            return

        if data == "profile_delete_final":
            await profile_handler.delete_final(update, context)
            return

        # ── ИНСТРУМЕНТЫ ──
        if data == "calc_start":
            await calc_handler.start(update, context)
            return

        if data == "age_start":
            await age_handler.handle(update, context)
            return

        if data == "mensur_start":
            await mensur_handler.handle(update, context)
            return

        if data == "reg_start":
            await regulating_handler.handle(update, context)
            return

        # ── О КЛУБЕ ──
        if data == "about":
            await query.answer()
            text = (
                "**ℹ️ О клубе**\n\n"
                "**Piano Technicians Club** — закрытое сообщество\n"
                "профессиональных фортепианных мастеров.\n\n"
                "🔹 Калькулятор басовых струн\n"
                "🔹 Атлас возрастов\n"
                "🔹 База мензур\n"
                "🔹 Регулировочные параметры\n\n"
                "🌐 piano-technicians.club"
            )
            kb = [
                [InlineKeyboardButton("🌐 Сайт клуба", url="https://piano-technicians.club")],
                [InlineKeyboardButton("◀️ Назад", callback_data="back_menu")],
            ]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
            return

    application.add_handler(CallbackQueryHandler(global_callback_router))

    logger.info("🚀 Бот готов к работе!")
    application.run_polling()


if __name__ == "__main__":
    main()