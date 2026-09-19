from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Case, CaseTag, CaseMedia, User
from app.schemas.case import CaseCreate, CaseResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/cases", tags=["cases"])


def case_to_response(case: Case) -> dict:
    return {
        "id": case.id,
        "user_id": case.user_id,
        "title": case.title,
        "symptom": case.symptom,
        "diagnosis": case.diagnosis,
        "solution": case.solution,
        "tools_used": case.tools_used,
        "difficulty": case.difficulty,
        "is_verified": case.is_verified,
        "view_count": case.view_count,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "tags": [t.tag for t in case.tags],
        "media": [{"id": m.id, "media_type": m.media_type, "url": m.url, "description": m.description} for m in case.media],
    }


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = Case(
        user_id=current_user.id,
        title=case_data.title,
        symptom=case_data.symptom,
        diagnosis=case_data.diagnosis,
        solution=case_data.solution,
        tools_used=case_data.tools_used,
        difficulty=case_data.difficulty,
    )
    db.add(case)
    db.flush()

    for tag in case_data.tags:
        db.add(CaseTag(case_id=case.id, tag=tag.tag))

    for media in case_data.media:
        db.add(CaseMedia(
            case_id=case.id,
            media_type=media.media_type,
            url=media.url,
            description=media.description
        ))

    db.commit()
    db.refresh(case)
    return case_to_response(case)


@router.get("/", response_model=List[CaseResponse])
def list_cases(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    cases = db.query(Case).order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
    return [case_to_response(c) for c in cases]


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.view_count += 1
    db.commit()
    db.refresh(case)
    return case_to_response(case)
