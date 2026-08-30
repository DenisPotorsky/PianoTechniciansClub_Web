from models.db_models import User
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class UserManagementService:
    def get_users_list(self, limit: int = 20) -> list[dict]:
        db = SessionLocal()
        try:
            db.expire_all()
            users = db.query(User).order_by(User.id.desc()).limit(limit).all()
            return [
                {
                    "id": u.id,
                    "telegram_id": u.telegram_id,
                    "name": u.first_name or u.username or "Без имени",
                    "email": u.email or "",
                    "is_approved": u.is_approved,
                    "is_admin": u.is_admin,
                    "is_super_admin": u.is_super_admin
                }
                for u in users
            ]
        except Exception as e:
            logger.error(f"❌ Ошибка списка: {e}", exc_info=True)
            return []
        finally:
            db.close()

    def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        db = SessionLocal()
        try:
            u = db.query(User).filter(User.telegram_id == telegram_id).first()
            if not u:
                return None
            return {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "name": u.first_name or u.username or "Без имени",
                "email": u.email or "",
                "is_approved": u.is_approved,
                "is_admin": u.is_admin,
                "is_super_admin": u.is_super_admin
            }
        finally:
            db.close()

    def get_pending_users(self) -> list[dict]:
        db = SessionLocal()
        try:
            db.expire_all()
            users = db.query(User).filter(
                User.is_approved == False,
                User.telegram_id.isnot(None)
            ).order_by(User.id.desc()).all()
            return [
                {"id": u.id, "telegram_id": u.telegram_id, "name": u.first_name or u.username or "Без имени"}
                for u in users
            ]
        except Exception as e:
            logger.error(f"❌ Ошибка получения заявок: {e}", exc_info=True)
            return []
        finally:
            db.close()

    def get_admin_ids(self) -> list[int]:
        db = SessionLocal()
        try:
            admins = db.query(User.telegram_id).filter(
                User.telegram_id.isnot(None),
                (User.is_admin == True) | (User.is_super_admin == True)
            ).all()
            return [a[0] for a in admins if a[0]]
        except Exception as e:
            logger.error(f"❌ Ошибка получения админов: {e}")
            return []
        finally:
            db.close()

    def approve_user(self, telegram_id: int) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.is_approved = True
                db.commit()
                logger.info(f"✅ Одобрен: {user.first_name} ({telegram_id})")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка одобрения: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def reject_user(self, telegram_id: int) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                db.delete(user)
                db.commit()
                logger.info(f"🚫 Отклонён и удалён: {user.first_name} ({telegram_id})")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка отклонения: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def update_user(self, telegram_id: int, field: str, value: str) -> bool:
        """Редактирует поле пользователя (first_name или email)"""
        if field not in ("first_name", "email"):
            return False
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                setattr(user, field, value)
                db.commit()
                logger.info(f"✏️ Обновлено {field} для {telegram_id}: {value}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка обновления: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def delete_user(self, telegram_id: int) -> bool:
        """Удаляет пользователя из базы"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                name = user.first_name
                db.delete(user)
                db.commit()
                logger.info(f"🗑️ Удалён пользователь: {name} ({telegram_id})")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка удаления: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def toggle_admin(self, telegram_id: int) -> bool | None:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.is_admin = not user.is_admin
                db.commit()
                return user.is_admin
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка смены админа: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def toggle_super_admin(self, telegram_id: int) -> bool | None:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.is_super_admin = not user.is_super_admin
                db.commit()
                return user.is_super_admin
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка смены супер-админа: {e}")
            db.rollback()
            return None
        finally:
            db.close()