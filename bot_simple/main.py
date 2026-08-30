import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes
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
from app.logger import setup_logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScopedUserRepository:
    def get_by_telegram_id(self, tid):
        db = SessionLocal()
        try:
            repo = UserRepository(db)
            return repo.get_by_telegram_id(tid)
        finally:
            db.close()

    def create(self, data):
        db = SessionLocal()
        try:
            repo = UserRepository(db)
            return repo.create(data)
        finally:
            db.close()


class ScopedSubscriptionRepository:
    def get_by_user_id(self, uid):
        db = SessionLocal()
        try:
            repo = SubscriptionRepository(db)
            return repo.get_by_user_id(uid)
        finally:
            db.close()

    def create(self, data):
        db = SessionLocal()
        try:
            repo = SubscriptionRepository(db)
            return repo.create(data)
        finally:
            db.close()

    def update(self, id, data):
        db = SessionLocal()
        try:
            repo = SubscriptionRepository(db)
            return repo.update(id, data)
        finally:
            db.close()


def main():
    config.validate()
    logger = setup_logger()
    logger.info("Конфигурация загружена успешно")

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
    admin_handler = AdminHandler(admin_service, user_mgmt_service, access_service, user_service)

    application.add_handler(CommandHandler("start", start_handler.handle))
    application.add_handler(CommandHandler("calc", calc_handler.handle))
    application.add_handler(CommandHandler("age", age_handler.handle))
    application.add_handler(CommandHandler("mensur", mensur_handler.handle))
    application.add_handler(CommandHandler("reg", regulating_handler.handle))
    application.add_handler(CommandHandler("admin", admin_handler.handle))

    application.add_handler(calc_handler.get_conversation_handler())
    application.add_handler(age_handler.get_conversation_handler())
    application.add_handler(mensur_handler.get_conversation_handler())
    application.add_handler(regulating_handler.get_conversation_handler())
    application.add_handler(admin_handler.get_edit_conversation_handler())

    async def global_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data = query.data
        user = update.effective_user
        db_user = user_service.get_by_telegram_id(user.id)

        # === ЗАЯВКА НА ВСТУПЛЕНИЕ ===
        if data == "apply_membership":
            existing = user_service.get_by_telegram_id(user.id)
            if existing:
                if not existing.is_approved:
                    await query.answer("⏳ Заявка уже подана!", show_alert=True)
                else:
                    await query.answer("✅ Вы уже участник!", show_alert=True)
                return

            user_service.create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name
            )

            admin_ids = user_mgmt_service.get_admin_ids()
            await notification_service.notify_admins_new_request(
                user_name=user.first_name or user.username or "Без имени",
                telegram_id=user.id,
                admin_ids=admin_ids
            )

            await query.edit_message_text(
                f"✅ **Заявка отправлена!**\n\n"
                f"Администратор получил уведомление и скоро рассмотрит вашу заявку.\n"
                f"Вы получите сообщение, когда вас одобрят.",
                parse_mode="Markdown"
            )
            await query.answer()

        # === ОДОБРЕНИЕ / ОТКЛОНЕНИЕ ИЗ УВЕДОМЛЕНИЯ ===
        elif data.startswith("approve_"):
            if not access_service.can_approve_users(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return

            tid = int(data.split("_")[1])
            success = user_mgmt_service.approve_user(tid)
            if success:
                await query.answer("✅ Пользователь одобрен!")
                await notification_service.notify_user_approved(tid)
                admin_ids = user_mgmt_service.get_admin_ids()
                approver_name = user.first_name or "Админ"
                await notification_service.notify_admins_user_approved(
                    user_name=f"ID:{tid}",
                    telegram_id=tid,
                    approved_by=approver_name,
                    admin_ids=admin_ids
                )
                try:
                    await admin_handler.show_pending_users(update, context)
                except Exception:
                    pass
            else:
                await query.answer("❌ Ошибка одобрения")

        elif data.startswith("reject_"):
            if not access_service.can_approve_users(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return

            tid = int(data.split("_")[1])
            success = user_mgmt_service.reject_user(tid)
            if success:
                await query.answer("🚫 Заявка отклонена")
                await notification_service.notify_user_rejected(tid)
                try:
                    await admin_handler.show_pending_users(update, context)
                except Exception:
                    pass
            else:
                await query.answer("❌ Ошибка отклонения")

        # === АДМИНКА ===
        elif data == "admin_refresh":
            stats = admin_service.get_statistics()
            text = (f"**Обновленная статистика:**\n"
                    f"• Всего пользователей: `{stats.get('total_users', 0)}`\n"
                    f"• Ожидают одобрения: `{stats.get('pending_users', 0)}`\n"
                    f"• Одобренных: `{stats.get('approved_users', 0)}`\n"
                    f"• Расчётов: `{stats.get('calculations', 0)}`")
            await query.edit_message_text(text, parse_mode="Markdown")
            await query.answer("✅ Статистика обновлена")

        elif data == "admin_panel":
            if not access_service.is_admin_panel_visible(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return
            await admin_handler.handle(update, context)
            await query.answer()

        elif data == "admin_pending":
            if not access_service.can_approve_users(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return
            await admin_handler.show_pending_users(update, context)
            await query.answer()

        elif data == "admin_users":
            if not access_service.is_admin_panel_visible(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return
            await admin_handler.show_users_list(update, context)
            await query.answer()

        elif data == "admin_admins":
            if not access_service.can_manage_admins(db_user):
                await query.answer("❌ Только супер-админ", show_alert=True)
                return
            await admin_handler.show_admins_management(update, context)
            await query.answer()

        elif data == "admin_back":
            await admin_handler.back_to_admin(update, context)

        elif data.startswith("user_detail_"):
            if not access_service.is_admin_panel_visible(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return
            await admin_handler.show_user_detail(update, context)
            await query.answer()

        elif data.startswith("confirm_delete_"):
            if not access_service.is_admin_panel_visible(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return
            await admin_handler.confirm_delete(update, context)
            await query.answer()

        elif data.startswith("do_delete_"):
            if not access_service.is_admin_panel_visible(db_user):
                await query.answer("❌ Нет прав", show_alert=True)
                return
            await admin_handler.do_delete(update, context)

        elif data.startswith("toggle_admin_"):
            if not access_service.can_manage_admins(db_user):
                await query.answer("❌ Только супер-админ", show_alert=True)
                return
            tid = int(data.split("_")[2])
            new_status = user_mgmt_service.toggle_admin(tid)
            if new_status is not None:
                role = "админом" if new_status else "пользователем"
                await query.answer(f"✅ Теперь {role}")
                await admin_handler.show_admins_management(update, context)
            else:
                await query.answer("❌ Пользователь не найден")

        elif data.startswith("toggle_super_"):
            if not access_service.can_manage_admins(db_user):
                await query.answer("❌ Только супер-админ", show_alert=True)
                return
            tid = int(data.split("_")[2])
            new_status = user_mgmt_service.toggle_super_admin(tid)
            if new_status is not None:
                role = "супер-админом" if new_status else "обычным админом"
                await query.answer(f"✅ Теперь {role}")
                await admin_handler.show_admins_management(update, context)
            else:
                await query.answer("❌ Пользователь не найден")

        # === ГЛАВНОЕ МЕНЮ ===
        elif data == "back_menu":
            await start_handler.handle(update, context)

        elif data == "about":
            await query.answer("Раздел в разработке", show_alert=True)

    application.add_handler(CallbackQueryHandler(global_callback_router))

    logger.info("🚀 Бот готов к работе!")
    application.run_polling()


if __name__ == "__main__":
    main()