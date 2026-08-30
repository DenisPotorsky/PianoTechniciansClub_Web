# bot/services/subscription_service.py
from typing import Optional
from datetime import datetime, timedelta
from models.db_models import User, Subscription
from repositories.subscription_repo import SubscriptionRepository
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    TRIAL_DAYS = 7

    def __init__(self, repo: SubscriptionRepository):
        self.repo = repo

    def get_by_user(self, user: User) -> Optional[Subscription]:
        return self.repo.get_by_user_id(user.id)

    def has_active_subscription(self, user: User) -> bool:
        sub = self.get_by_user(user)
        if not sub or not sub.is_active:
            return False
        if sub.expires_at < datetime.now():
            return False
        return True

    def start_trial(self, user: User) -> Subscription:
        existing = self.repo.get_by_user_id(user.id)
        if existing:
            if existing.trial_start:
                raise ValueError("Пробный период уже использован")
            # Активируем триал на существующей записи
            existing.trial_start = datetime.now()
            existing.trial_end = datetime.now() + timedelta(days=self.TRIAL_DAYS)
            existing.expires_at = existing.trial_end
            existing.is_active = True
            return self.repo.update(existing.id, {
                "trial_start": existing.trial_start,
                "trial_end": existing.trial_end,
                "expires_at": existing.expires_at,
                "is_active": True
            })

        # Создаем новую
        now = datetime.now()
        return self.repo.create({
            "user_id": user.id,
            "is_active": True,
            "starts_at": now,
            "expires_at": now + timedelta(days=self.TRIAL_DAYS),
            "trial_start": now,
            "trial_end": now + timedelta(days=self.TRIAL_DAYS)
        })