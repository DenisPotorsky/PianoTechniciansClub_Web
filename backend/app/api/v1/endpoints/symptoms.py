from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Symptom, User
from app.schemas.case import SymptomCreate, SymptomResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/symptoms", tags=["symptoms"])


@router.get("/", response_model=List[SymptomResponse])
def list_symptoms(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Symptom)
    if category:
        query = query.filter(Symptom.category == category)
    if search:
        query = query.filter(Symptom.name.ilike(f"%{search}%"))
    return query.order_by(Symptom.name).all()


@router.post("/", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED)
def create_symptom(
    data: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Symptom).filter(Symptom.name.ilike(data.name)).first()
    if existing:
        return existing
    symptom = Symptom(name=data.name, category=data.category, description=data.description)
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    return symptom
