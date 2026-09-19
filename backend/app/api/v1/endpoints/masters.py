from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
import math
import os
import uuid
import shutil
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import MasterProfile, MasterReview, User
from app.core.security import get_current_user

router = APIRouter(prefix="/masters", tags=["masters"])


class MasterProfileCreate(BaseModel):
    specialization: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None


class MasterProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    specialization: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    rating: float
    review_count: int
    is_verified: bool

    class Config:
        from_attributes = True


def profile_to_response(profile: MasterProfile) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "first_name": profile.user.first_name,
        "last_name": profile.user.last_name,
        "specialization": profile.specialization,
        "city": profile.city,
        "address": profile.address,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "bio": profile.bio,
        "photo_url": profile.photo_url,
        "phone": profile.phone,
        "telegram": profile.telegram,
        "rating": profile.rating,
        "review_count": profile.review_count,
        "is_verified": profile.is_verified,
    }


@router.post("/", response_model=MasterProfileResponse, status_code=status.HTTP_201_CREATED)
def create_master_profile(
    data: MasterProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(MasterProfile).filter(MasterProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(400, "Master profile already exists")

    profile = MasterProfile(user_id=current_user.id, **data.model_dump(exclude_unset=True))
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile_to_response(profile)


@router.get("/")
def list_masters(
    city: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
    lat: Optional[float] = Query(None, description="Широта пользователя"),
    lng: Optional[float] = Query(None, description="Долгота пользователя"),
    radius_km: Optional[float] = Query(None, description="Радиус поиска в км"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(MasterProfile).filter(MasterProfile.is_active == True)
    if city:
        query = query.filter(MasterProfile.city.ilike(f"%{city}%"))
    if specialization:
        query = query.filter(MasterProfile.specialization.ilike(f"%{specialization}%"))
    
    # Geo filtering using Haversine in Python
    if lat is not None and lng is not None and radius_km is not None:
        query = query.filter(
            MasterProfile.latitude.isnot(None),
            MasterProfile.longitude.isnot(None)
        )
        profiles = query.order_by(MasterProfile.is_verified.desc(), MasterProfile.rating.desc()).all()
        
        R = 6371.0
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)
        
        response = []
        for p in profiles:
            dlat = math.radians(p.latitude - lat)
            dlng = math.radians(p.longitude - lng)
            a = math.sin(dlat/2)**2 + math.cos(lat_rad) * math.cos(math.radians(p.latitude)) * math.sin(dlng/2)**2
            distance = R * 2 * math.asin(math.sqrt(a))
            if distance <= radius_km:
                resp = profile_to_response(p)
                resp["distance_km"] = round(distance, 1)
                response.append(resp)
        return response[skip:skip+limit]
    
    profiles = query.order_by(MasterProfile.is_verified.desc(), MasterProfile.rating.desc()).offset(skip).limit(limit).all()
    return [profile_to_response(p) for p in profiles]


@router.get("/{master_id}", response_model=MasterProfileResponse)
def get_master(master_id: int, db: Session = Depends(get_db)):
    profile = db.query(MasterProfile).filter(MasterProfile.id == master_id).first()
    if not profile:
        raise HTTPException(404, "Master not found")
    return profile_to_response(profile)


@router.post("/me/photo")
async def upload_my_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Только JPEG, PNG или WebP")
    
    # Validate size (max 2MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(400, "Файл слишком большой (макс. 2 МБ)")
    
    # Save file
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"master_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # Update profile
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(404, "Профиль мастера не найден")
    
    # Delete old photo
    if profile.photo_url:
        old_path = profile.photo_url.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)
    
    profile.photo_url = f"/uploads/{filename}"
    db.commit()
    db.refresh(profile)
    
    return {"photo_url": profile.photo_url}


@router.get("/me", response_model=MasterProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(404, "Master profile not found")
    return profile_to_response(profile)


@router.put("/me", response_model=MasterProfileResponse)
def update_my_profile(
    data: MasterProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(404, "Master profile not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile_to_response(profile)


class ReviewCreate(BaseModel):
    rating: int
    text: Optional[str] = None
    photo_url: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    master_id: int
    user_id: int
    first_name: str
    rating: int
    text: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


def recalculate_rating(db: Session, master_id: int):
    """Пересчитывает средний рейтинг и количество отзывов"""
    reviews = db.query(MasterReview).filter(MasterReview.master_id == master_id).all()
    count = len(reviews)
    avg = sum(r.rating for r in reviews) / count if count > 0 else 0.0
    
    profile = db.query(MasterProfile).filter(MasterProfile.id == master_id).first()
    if profile:
        profile.review_count = count
        profile.rating = round(avg, 2)
        db.commit()


@router.post("/{master_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    master_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(400, "Rating must be between 1 and 5")
    
    master = db.query(MasterProfile).filter(MasterProfile.id == master_id).first()
    if not master:
        raise HTTPException(404, "Master not found")
    
    # Нельзя оставить отзыв самому себе
    if master.user_id == current_user.id:
        raise HTTPException(400, "Cannot review yourself")
    
    # Один пользователь = один отзыв
    existing = db.query(MasterReview).filter(
        MasterReview.master_id == master_id,
        MasterReview.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(400, "You already reviewed this master")
    
    review = MasterReview(
        master_id=master_id,
        user_id=current_user.id,
        **data.model_dump(exclude_unset=True)
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    recalculate_rating(db, master_id)
    
    return {
        "id": review.id,
        "master_id": review.master_id,
        "user_id": review.user_id,
        "first_name": current_user.first_name,
        "rating": review.rating,
        "text": review.text,
        "photo_url": review.photo_url,
        "created_at": review.created_at,
    }


@router.get("/{master_id}/reviews", response_model=List[ReviewResponse])
def list_reviews(master_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    reviews = (
        db.query(MasterReview)
        .filter(MasterReview.master_id == master_id)
        .order_by(MasterReview.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for r in reviews:
        result.append({
            "id": r.id,
            "master_id": r.master_id,
            "user_id": r.user_id,
            "first_name": r.user.first_name,
            "rating": r.rating,
            "text": r.text,
            "photo_url": r.photo_url,
            "created_at": r.created_at,
        })
    return result


@router.patch("/{master_id}/verify", response_model=MasterProfileResponse)
def verify_master(
    master_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin and not current_user.is_super_admin:
        raise HTTPException(403, "Admin access required")
    
    profile = db.query(MasterProfile).filter(MasterProfile.id == master_id).first()
    if not profile:
        raise HTTPException(404, "Master not found")
    
    profile.is_verified = True
    db.commit()
    db.refresh(profile)
    return profile_to_response(profile)


@router.patch("/{master_id}/unverify", response_model=MasterProfileResponse)
def unverify_master(
    master_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin and not current_user.is_super_admin:
        raise HTTPException(403, "Admin access required")
    
    profile = db.query(MasterProfile).filter(MasterProfile.id == master_id).first()
    if not profile:
        raise HTTPException(404, "Master not found")
    
    profile.is_verified = False
    db.commit()
    db.refresh(profile)
    return profile_to_response(profile)
