from typing import Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from models.db_models import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def get_or_create(self, telegram_id: int, defaults: dict) -> User:
        user = self.get_by_telegram_id(telegram_id)
        if not user:
            data = {"telegram_id": telegram_id, **defaults}
            user = self.create(data)
        return user