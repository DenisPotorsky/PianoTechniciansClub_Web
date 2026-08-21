from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, RegulatingParam, AccessRequest, Brand
from app.core.security import require_admin, require_super_admin

router = APIRouter()


# ============ СТАТИСТИКА ============
@router.get("/stats")
async def get_stats(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Получить статистику по клубу"""
    total_users = db.query(User).count()
    subscribed_users = db.query(User).filter(User.is_subscribed == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    pending_requests = db.query(AccessRequest).filter(AccessRequest.status == "pending").count()

    return {
        "total_users": total_users,
        "subscribed_users": subscribed_users,
        "admin_users": admin_users,
        "pending_requests": pending_requests
    }


# ============ ПОЛЬЗОВАТЕЛИ ============
@router.get("/users")
async def get_users(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Получить всех пользователей"""
    users = db.query(User).all()
    return [{
        "id": u.id,
        "telegram_id": u.telegram_id,
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "is_subscribed": u.is_subscribed,
        "is_admin": u.is_admin,
        "is_super_admin": u.is_super_admin,
        "created_at": u.created_at
    } for u in users]


@router.put("/users/{user_id}")
async def update_user(
        user_id: int,
        user_data: dict,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    """Обновить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    for key, value in user_data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)

    db.commit()
    return {"message": "Пользователь обновлён"}


@router.delete("/users/{user_id}")
async def delete_user(
        user_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    """Удалить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя удалить супер-админа")

    db.delete(user)
    db.commit()
    return {"message": "Пользователь удалён"}


# ============ БЕЛЫЙ СПИСОК ============
@router.get("/whitelist")
async def get_whitelist(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Получить список администраторов (белый список)"""
    admins = db.query(User).filter(
        (User.is_admin == True) | (User.is_super_admin == True)
    ).all()

    return [{
        "id": a.id,
        "telegram_id": a.telegram_id,
        "username": a.username,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "is_admin": a.is_admin,
        "is_super_admin": a.is_super_admin
    } for a in admins]


@router.post("/whitelist/add")
async def add_to_whitelist(
        telegram_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    """Добавить пользователя в белый список"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_admin = True
    db.commit()
    return {"message": "Пользователь добавлен в белый список"}


@router.post("/whitelist/remove")
async def remove_from_whitelist(
        telegram_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    """Удалить пользователя из белого списка"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя удалить супер-админа")

    user.is_admin = False
    db.commit()
    return {"message": "Пользователь удалён из белого списка"}


# ============ ЗАЯВКИ ============
@router.get("/requests")
async def get_requests(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Получить все заявки"""
    requests = db.query(AccessRequest).all()
    return [{
        "id": r.id,
        "user_id": r.user_id,
        "username": r.user.username if r.user else None,
        "full_name": r.full_name,
        "message": r.message,
        "status": r.status,
        "created_at": r.created_at
    } for r in requests]


@router.post("/requests/{request_id}/approve")
async def approve_request(
        request_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Одобрить заявку"""
    request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    request.status = "approved"
    request.processed_by = current_user.id

    # Если есть пользователь с таким email
    if request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            user.is_subscribed = True

    db.commit()
    return {"message": "Заявка одобрена"}


@router.post("/requests/{request_id}/reject")
async def reject_request(
        request_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Отклонить заявку"""
    request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    request.status = "rejected"
    request.processed_by = current_user.id
    db.commit()
    return {"message": "Заявка отклонена"}


# ============ БРЕНДЫ (АТЛАС) ============
@router.get("/brands")
async def get_brands_admin(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Получить все бренды (для админки)"""
    brands = db.query(Brand).all()
    return [{
        "id": b.id,
        "name": b.name,
        "country": b.country,
        "type": b.type,
        "info": b.info,
        "ranges_count": len(b.serial_ranges) if b.serial_ranges else 0
    } for b in brands]


@router.delete("/brands/{brand_id}")
async def delete_brand(
        brand_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Удалить бренд"""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")

    db.delete(brand)
    db.commit()
    return {"message": "Бренд удалён"}