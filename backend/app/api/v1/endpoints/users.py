from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import User, Calculation
from app.core.security import require_member
from loguru import logger

router = APIRouter()


class ProfileUpdate(BaseModel):
    first_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None


@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db)
):
    logger.info(f"📝 Обновление профиля пользователя {current_user.id}")

    if data.email:
        existing = db.query(User).filter(
            func.lower(User.email) == func.lower(data.email),
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email уже используется")

    current_user.first_name = data.first_name
    current_user.email = data.email
    current_user.phone = data.phone
    current_user.city = data.city

    db.commit()
    db.refresh(current_user)

    logger.success(f"✅ Профиль {current_user.id} обновлён")
    return {"message": "Профиль обновлён"}


@router.get("/stats")
async def get_stats(current_user: User = Depends(require_member), db: Session = Depends(get_db)):
    count = db.query(func.count(Calculation.id)).filter(
        Calculation.user_id == current_user.id
    ).scalar() or 0
    last = db.query(func.max(Calculation.created_at)).filter(
        Calculation.user_id == current_user.id
    ).scalar()
    return {"count": count, "last_date": last}


@router.post("/logout-club")
async def logout_club(current_user: User = Depends(require_member), db: Session = Depends(get_db)):
    logger.info(f"🚪 Пользователь {current_user.id} выходит из клуба")
    db.query(Calculation).filter(Calculation.user_id == current_user.id).delete()
    current_user.is_approved = False
    current_user.is_admin = False
    current_user.is_super_admin = False
    db.commit()
    return {"message": "Вы вышли из клуба"}


@router.delete("/profile")
async def delete_profile(current_user: User = Depends(require_member), db: Session = Depends(get_db)):
    logger.warning(f"🗑️ Удаление профиля {current_user.id}")
    db.delete(current_user)
    db.commit()
    return {"message": "Профиль удалён"}