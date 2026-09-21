from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Tag, User
from app.schemas.case import TagCreate, TagResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagResponse])
def list_tags(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))
    return query.order_by(Tag.name).all()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Tag).filter(Tag.name.ilike(data.name)).first()
    if existing:
        return existing
    tag = Tag(name=data.name, category=data.category)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
