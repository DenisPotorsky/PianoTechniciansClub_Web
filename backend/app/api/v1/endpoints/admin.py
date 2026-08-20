from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Calculation, Brand, SerialRange, AccessRequest, Notification
from app.core.security import require_admin, require_super_admin, get_password_hash
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])


# ============ СХЕМЫ ============
class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    is_subscribed: bool
    is_admin: bool
    is_super_admin: bool
    created_at: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_subscribed: Optional[bool] = None
    is_admin: Optional[bool] = None


class StatsResponse(BaseModel):
    total_users: int
    subscribed_users: int
    admin_users: int
    total_calculations: int
    total_brands: int
    pending_requests: int


class BrandCreate(BaseModel):
    name: str
    country: str
    type: str
    info: Optional[str] = None


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    info: Optional[str] = None


class SerialRangeCreate(BaseModel):
    serial_start: int
    serial_end: int
    year: int


class SerialRangeUpdate(BaseModel):
    serial_start: Optional[int] = None
    serial_end: Optional[int] = None
    year: Optional[int] = None


# ============ СТАТИСТИКА ============
@router.get("/stats", response_model=StatsResponse)
async def get_stats(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    subscribed_users = db.query(User).filter(User.is_subscribed == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    total_calculations = db.query(Calculation).count()
    total_brands = db.query(Brand).count()
    pending_requests = db.query(AccessRequest).filter(AccessRequest.status == "pending").count()

    return StatsResponse(
        total_users=total_users,
        subscribed_users=subscribed_users,
        admin_users=admin_users,
        total_calculations=total_calculations,
        total_brands=total_brands,
        pending_requests=pending_requests
    )


# ============ ПОЛЬЗОВАТЕЛИ ============
@router.get("/users", response_model=List[UserResponse])
async def get_users(
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    query = db.query(User)
    if search:
        query = query.filter(
            User.username.ilike(f"%{search}%") |
            User.first_name.ilike(f"%{search}%") |
            User.last_name.ilike(f"%{search}%") |
            User.telegram_id.ilike(f"%{search}%")
        )
    users = query.offset(skip).limit(limit).all()

    return [
        UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_subscribed=user.is_subscribed,
            is_admin=user.is_admin,
            is_super_admin=user.is_super_admin,
            created_at=user.created_at.isoformat() if user.created_at else ""
        )
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_subscribed=user.is_subscribed,
        is_admin=user.is_admin,
        is_super_admin=user.is_super_admin,
        created_at=user.created_at.isoformat() if user.created_at else ""
    )


@router.put("/users/{user_id}")
async def update_user(
        user_id: int,
        data: UserUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Нельзя менять супер-админа (кроме супер-админа)
    if user.is_super_admin and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя редактировать супер-админа")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return {"message": f"Пользователь {user.username} обновлён"}


@router.delete("/users/{user_id}")
async def delete_user(
        user_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя удалить супер-админа")

    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="Нельзя удалить себя")

    db.delete(user)
    db.commit()
    return {"message": f"Пользователь удалён"}


# ============ БЕЛЫЙ СПИСОК (АДМИНЫ) ============
@router.get("/whitelist")
async def get_whitelist(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    admins = db.query(User).filter(User.is_admin == True).all()
    return [
        {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_super_admin": u.is_super_admin
        }
        for u in admins
    ]


@router.post("/whitelist/add")
async def add_to_whitelist(
        telegram_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    """Добавить пользователя в белый список (админом) — только для супер-админа"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_admin:
        return {"message": f"Пользователь {user.username} уже является админом"}

    user.is_admin = True
    user.is_subscribed = True
    db.commit()

    notification = Notification(
        user_id=user.id,
        title="🌟 Вы стали администратором!",
        message=f"Супер-админ {current_user.username} назначил вас администратором клуба. Добро пожаловать в команду! 🎉",
        type="info"
    )
    db.add(notification)
    db.commit()

    return {"message": f"✅ Пользователь {user.username} добавлен в белый список (админ)"}


@router.post("/whitelist/remove")
async def remove_from_whitelist(
        telegram_id: int,
        current_user: User = Depends(require_super_admin),
        db: Session = Depends(get_db)
):
    """Удалить пользователя из белого списка — только для супер-админа"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя удалить супер-админа")

    if not user.is_admin:
        return {"message": f"Пользователь {user.username} не является админом"}

    user.is_admin = False
    user.is_subscribed = False
    db.commit()

    notification = Notification(
        user_id=user.id,
        title="⚠️ Вы больше не администратор",
        message=f"Супер-админ {current_user.username} лишил вас прав администратора.",
        type="info"
    )
    db.add(notification)
    db.commit()

    return {"message": f"✅ Пользователь {user.username} удалён из белого списка"}


# ============ ЗАЯВКИ ============
@router.get("/requests")
async def get_requests(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db),
        status: Optional[str] = None
):
    query = db.query(AccessRequest)
    if status:
        query = query.filter(AccessRequest.status == status)
    requests = query.order_by(AccessRequest.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "username": r.user.username,
            "full_name": f"{r.user.first_name} {r.user.last_name or ''}",
            "message": r.message,
            "status": r.status,
            "created_at": r.created_at.isoformat()
        }
        for r in requests
    ]


@router.post("/requests/{request_id}/{action}")
async def process_request(
        request_id: int,
        action: str,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Одобрить или отклонить заявку"""
    access_request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not access_request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if access_request.status != "pending":
        raise HTTPException(status_code=400, detail="Заявка уже обработана")

    user = db.query(User).filter(User.id == access_request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if action == "approve":
        user.is_subscribed = True
        access_request.status = "approved"
        access_request.processed_by = current_user.id
        access_request.processed_at = datetime.utcnow()

        notification = Notification(
            user_id=user.id,
            title="✅ Доступ подтверждён!",
            message=f"Ваш доступ в клуб подтверждён администратором {current_user.username}. Добро пожаловать! 🎹",
            type="access_approved"
        )
        db.add(notification)
        db.commit()
        return {"message": f"✅ Заявка одобрена. Пользователь {user.username} получил доступ"}

    elif action == "reject":
        access_request.status = "rejected"
        access_request.processed_by = current_user.id
        access_request.processed_at = datetime.utcnow()

        notification = Notification(
            user_id=user.id,
            title="❌ Доступ отклонён",
            message=f"Ваш доступ в клуб отклонён администратором {current_user.username}",
            type="access_rejected"
        )
        db.add(notification)
        db.commit()
        return {"message": f"❌ Заявка отклонена"}

    else:
        raise HTTPException(status_code=400, detail="Неверное действие")


# ============ БРЕНДЫ ============
@router.get("/brands")
async def get_all_brands(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    brands = db.query(Brand).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "country": b.country,
            "type": b.type,
            "info": b.info,
            "ranges_count": db.query(SerialRange).filter(SerialRange.brand_id == b.id).count()
        }
        for b in brands
    ]


@router.post("/brands")
async def add_brand(
        data: BrandCreate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    existing = db.query(Brand).filter(Brand.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Бренд уже существует")

    brand = Brand(
        name=data.name,
        country=data.country,
        type=data.type,
        info=data.info
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return {"message": f"Бренд '{brand.name}' добавлен", "id": brand.id}


@router.put("/brands/{brand_id}")
async def update_brand(
        brand_id: int,
        data: BrandUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(brand, field, value)

    db.commit()
    db.refresh(brand)
    return {"message": f"Бренд '{brand.name}' обновлён"}


@router.delete("/brands/{brand_id}")
async def delete_brand(
        brand_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")

    db.query(SerialRange).filter(SerialRange.brand_id == brand_id).delete()
    db.delete(brand)
    db.commit()
    return {"message": f"Бренд '{brand.name}' удалён"}


# ============ ДИАПАЗОНЫ СЕРИЙНЫХ НОМЕРОВ ============
@router.get("/brands/{brand_id}/ranges")
async def get_brand_ranges(
        brand_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    ranges = db.query(SerialRange).filter(SerialRange.brand_id == brand_id).all()
    return [
        {
            "id": r.id,
            "serial_start": r.serial_start,
            "serial_end": r.serial_end,
            "year": r.year
        }
        for r in ranges
    ]


@router.post("/brands/{brand_id}/ranges")
async def add_serial_range(
        brand_id: int,
        data: SerialRangeCreate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Бренд не найден")

    serial_range = SerialRange(
        brand_id=brand_id,
        serial_start=data.serial_start,
        serial_end=data.serial_end,
        year=data.year
    )
    db.add(serial_range)
    db.commit()
    db.refresh(serial_range)
    return {"message": "Диапазон добавлен", "id": serial_range.id}


@router.put("/brands/ranges/{range_id}")
async def update_serial_range(
        range_id: int,
        data: SerialRangeUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    serial_range = db.query(SerialRange).filter(SerialRange.id == range_id).first()
    if not serial_range:
        raise HTTPException(status_code=404, detail="Диапазон не найден")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(serial_range, field, value)

    db.commit()
    db.refresh(serial_range)
    return {"message": "Диапазон обновлён"}


@router.delete("/brands/ranges/{range_id}")
async def delete_serial_range(
        range_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    serial_range = db.query(SerialRange).filter(SerialRange.id == range_id).first()
    if not serial_range:
        raise HTTPException(status_code=404, detail="Диапазон не найден")

    db.delete(serial_range)
    db.commit()
    return {"message": "Диапазон удалён"}


# ============ РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ ============
@router.put("/users/{user_id}")
async def update_user(
        user_id: int,
        data: UserUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Обновить данные пользователя (только для админов)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Нельзя редактировать супер-админа (кроме супер-админа)
    if user.is_super_admin and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя редактировать супер-админа")

    # Нельзя редактировать себя (кроме супер-админа)
    if user.id == current_user.id and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя редактировать себя")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return {"message": f"Пользователь {user.username} обновлён"}


@router.put("/users/{user_id}/password")
async def reset_user_password(
        user_id: int,
        password: str,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Сбросить пароль пользователя (только для админов)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя менять пароль супер-админа")

    user.hashed_password = get_password_hash(password)
    db.commit()
    return {"message": f"Пароль для {user.username} сброшен"}


# ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============
@router.put("/users/{user_id}/toggle-subscription")
async def toggle_subscription(
        user_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Переключить подписку пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_super_admin and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нельзя изменять суперадмина")

    user.is_subscribed = not user.is_subscribed
    db.commit()
    status = "активирована" if user.is_subscribed else "деактивирована"
    return {"message": f"Подписка {status} для {user.username}"}


@router.post("/users/{user_id}/reset-password")
async def reset_password(
        user_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    """Сбросить пароль пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_password = "temp123"
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": f"Пароль сброшен на: {new_password}"}