from models.db_models import User
from app.database import SessionLocal
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)


class UserManagementService:
    """Сервис управления пользователями для админ-панели бота"""

    def _user_to_dict(self, u: User) -> dict:
        return {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "name": u.first_name or u.username or "Без имени",
            "last_name": getattr(u, "last_name", "") or "",
            "email": u.email or "",
            "phone": u.phone or "",
            "city": u.city or "",
            "is_approved": u.is_approved,
            "is_admin": u.is_admin,
            "is_super_admin": u.is_super_admin,
            "created_at": u.created_at.strftime("%d.%m.%Y") if u.created_at else "—",
        }

    def get_users_list(self, limit: int = 10, offset: int = 0, search: str = None) -> list[dict]:
        db = SessionLocal()
        try:
            db.expire_all()
            query = db.query(User).order_by(User.id.desc())
            if search:
                pattern = f"%{search}%"
                query = query.filter(
                    (User.first_name.ilike(pattern))
                    | (User.email.ilike(pattern))
                    | (User.phone.ilike(pattern))
                    | (User.city.ilike(pattern))
                )
            users = query.offset(offset).limit(limit).all()
            return [self._user_to_dict(u) for u in users]
        except Exception as e:
            logger.error(f"❌ Ошибка списка: {e}", exc_info=True)
            return []
        finally:
            db.close()

    def get_users_count(self, search: str = None) -> int:
        db = SessionLocal()
        try:
            query = db.query(func.count(User.id))
            if search:
                pattern = f"%{search}%"
                query = query.filter(
                    (User.first_name.ilike(pattern))
                    | (User.email.ilike(pattern))
                    | (User.phone.ilike(pattern))
                    | (User.city.ilike(pattern))
                )
            return query.scalar() or 0
        except Exception as e:
            logger.error(f"❌ Ошибка подсчёта: {e}")
            return 0
        finally:
            db.close()

    def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        db = SessionLocal()
        try:
            u = db.query(User).filter(User.telegram_id == telegram_id).first()
            if not u:
                return None
            return self._user_to_dict(u)
        except Exception as e:
            logger.error(f"❌ Ошибка получения: {e}")
            return None
        finally:
            db.close()

    def get_pending_users(self) -> list[dict]:
        db = SessionLocal()
        try:
            db.expire_all()
            users = (
                db.query(User)
                .filter(User.is_approved == False, User.telegram_id.isnot(None))
                .order_by(User.id.desc())
                .all()
            )
            return [
                {
                    "id": u.id,
                    "telegram_id": u.telegram_id,
                    "name": u.first_name or u.username or "Без имени",
                    "email": u.email or "",
                    "city": u.city or "",
                    "created_at": u.created_at.strftime("%d.%m.%Y") if u.created_at else "—",
                }
                for u in users
            ]
        except Exception as e:
            logger.error(f"❌ Ошибка заявок: {e}", exc_info=True)
            return []
        finally:
            db.close()

    def get_admin_ids(self) -> list[int]:
        db = SessionLocal()
        try:
            admins = (
                db.query(User.telegram_id)
                .filter(
                    User.telegram_id.isnot(None),
                    (User.is_admin == True) | (User.is_super_admin == True),
                )
                .all()
            )
            return [a[0] for a in admins if a[0]]
        except Exception as e:
            logger.error(f"❌ Ошибка админов: {e}")
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
                logger.info(f"🚫 Отклонён: {user.first_name} ({telegram_id})")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка отклонения: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def toggle_approve(self, telegram_id: int) -> bool | None:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.is_approved = not user.is_approved
                db.commit()
                return user.is_approved
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка статуса: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def update_user(self, telegram_id: int, field: str, value: str) -> bool:
        allowed = ("first_name", "last_name", "email", "phone", "city", "is_approved", "is_admin")
        if field not in allowed:
            return False
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                setattr(user, field, value)
                db.commit()
                logger.info(f"✏️ {field} обновлено для {telegram_id}: {value}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка обновления: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def delete_user(self, telegram_id: int) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                name = user.first_name
                db.delete(user)
                db.commit()
                logger.info(f"🗑️ Удалён: {name} ({telegram_id})")
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
            logger.error(f"❌ Ошибка админа: {e}")
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
            logger.error(f"❌ Ошибка супер-админа: {e}")
            db.rollback()
            return None
        finally:
            db.close()