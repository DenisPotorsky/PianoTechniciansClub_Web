from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import User
from app.core.security import require_member

router = APIRouter()


class ProfileUpdate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: str
    email: str


@router.put("/profile")
async def update_profile(
        data: ProfileUpdate,
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    """Обновление профиля пользователя"""

    # Проверяем, не занят ли username другим пользователем
    existing = db.query(User).filter(
        func.lower(User.username) == func.lower(data.username),
        User.id != current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")

    # Проверяем, не занят ли email другим пользователем
    existing = db.query(User).filter(
        func.lower(User.email) == func.lower(data.email),
        User.id != current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email уже используется")

    # Обновляем
    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    current_user.username = data.username
    current_user.email = data.email
    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "username": current_user.username,
        "email": current_user.email,
        "message": "Профиль обновлён"
    }