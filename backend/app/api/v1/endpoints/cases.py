from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Case, CaseTag, CaseMedia, User
from app.schemas.case import CaseCreate, CaseResponse
from app.core.security import get_current_user
from app.services.rag_service import rag_service

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
    
    # Индексируем в векторную БД для RAG-поиска
    try:
        rag_service.index_case(
            case_id=case.id,
            title=case.title,
            symptom=case.symptom,
            solution=case.solution,
            tags=[t.tag for t in case.tags]
        )
    except Exception as e:
        print(f"⚠️ RAG индексация не удалась: {e}")
    
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
    
    # Индексируем в векторную БД для RAG-поиска
    try:
        rag_service.index_case(
            case_id=case.id,
            title=case.title,
            symptom=case.symptom,
            solution=case.solution,
            tags=[t.tag for t in case.tags]
        )
    except Exception as e:
        print(f"⚠️ RAG индексация не удалась: {e}")
    
    return case_to_response(case)


@router.put("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: int,
    title: str = None,
    symptom: str = None,
    diagnosis: str = None,
    solution: str = None,
    tools_used: str = None,
    difficulty: str = None,
    change_summary: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Сохраняем текущую версию перед обновлением
    from app.models import CaseVersion
    max_version = db.query(func.max(CaseVersion.version)).filter(
        CaseVersion.case_id == case_id
    ).scalar() or 0

    old_version = CaseVersion(
        case_id=case_id,
        version=max_version + 1,
        title=case.title,
        symptom=case.symptom,
        diagnosis=case.diagnosis,
        solution=case.solution,
        tools_used=case.tools_used,
        difficulty=case.difficulty,
        edited_by=current_user.id,
        change_summary=change_summary or "Обновление кейса",
    )
    db.add(old_version)

    # Обновляем кейс
    if title is not None: case.title = title
    if symptom is not None: case.symptom = symptom
    if diagnosis is not None: case.diagnosis = diagnosis
    if solution is not None: case.solution = solution
    if tools_used is not None: case.tools_used = tools_used
    if difficulty is not None: case.difficulty = difficulty

    db.commit()
    db.refresh(case)
    return case_to_response(case)


@router.get("/{case_id}/versions")
def get_case_versions(case_id: int, db: Session = Depends(get_db)):
    from app.models import CaseVersion
    versions = db.query(CaseVersion).filter(
        CaseVersion.case_id == case_id
    ).order_by(CaseVersion.version.desc()).all()

    return [
        {
            "id": v.id,
            "version": v.version,
            "title": v.title,
            "symptom": v.symptom,
            "diagnosis": v.diagnosis,
            "solution": v.solution,
            "tools_used": v.tools_used,
            "difficulty": v.difficulty,
            "edited_by": v.edited_by,
            "change_summary": v.change_summary,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]
