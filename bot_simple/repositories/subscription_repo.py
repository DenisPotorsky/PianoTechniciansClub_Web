from typing import Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from models.db_models import Subscription

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db: Session):
        super().__init__(Subscription, db)

    def get_by_user_id(self, user_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(Subscription.user_id == user_id).first()