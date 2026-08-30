# bot/services/user_service.py
from typing import Optional
from repositories.user_repo import UserRepository
from models.db_models import User
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.repo.get_by_telegram_id(telegram_id)

    def create_user(self, telegram_id: int, username: str = None, first_name: str = None):
        """Создаёт нового пользователя с is_approved=False"""
        from models.db_models import User
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name or "Без имени",
                is_approved=False,
                is_admin=False,
                is_super_admin=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя: {e}")
            db.rollback()
            return None
        finally:
            db.close()