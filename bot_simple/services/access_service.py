from typing import Tuple
from models.db_models import User


class AccessService:
    """Иерархия прав: Супер-админ > Админ > Одобренный > Заявка"""

    def has_access(self, user: User) -> Tuple[bool, str]:
        if not user or not user.id:
            return False, "not_registered"

        if not user.is_approved:
            return False, "pending_approval"

        return True, "approved"

    def can_manage_admins(self, user: User) -> bool:
        return user is not None and user.is_super_admin

    def can_approve_users(self, user: User) -> bool:
        return user is not None and (user.is_admin or user.is_super_admin)

    def is_admin_panel_visible(self, user: User) -> bool:
        return user is not None and (user.is_admin or user.is_super_admin)