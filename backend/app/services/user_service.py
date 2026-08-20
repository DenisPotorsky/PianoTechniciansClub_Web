from sqlalchemy.orm import Session
from app.models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_telegram_id(self, telegram_id: int):
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def create_user_with_password(self, telegram_id: int, username: str, first_name: str, last_name: str = None,
                                  hashed_password: str = None):
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            is_subscribed=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user