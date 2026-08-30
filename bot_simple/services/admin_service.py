from sqlalchemy import func
from models.db_models import User, Calculation
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


class AdminService:
    def get_statistics(self) -> dict:
        db = SessionLocal()
        try:
            # Принудительно обновляем сессию, чтобы видеть свежие данные
            db.expire_all()

            total_users = db.query(func.count(User.id)).scalar() or 0
            pending_users = db.query(func.count(User.id)).filter(User.is_approved == False).scalar() or 0
            approved_users = db.query(func.count(User.id)).filter(User.is_approved == True).scalar() or 0
            total_calculations = db.query(func.count(Calculation.id)).scalar() or 0

            logger.info(
                f"📊 Статистика БД: Всего={total_users}, Ожид={pending_users}, Одобр={approved_users}, Расч={total_calculations}")

            return {
                "total_users": total_users,
                "pending_users": pending_users,
                "approved_users": approved_users,
                "calculations": total_calculations
            }
        except Exception as e:
            logger.error(f"❌ Ошибка статистики: {e}", exc_info=True)
            return {"total_users": 0, "pending_users": 0, "approved_users": 0, "calculations": 0}
        finally:
            db.close()