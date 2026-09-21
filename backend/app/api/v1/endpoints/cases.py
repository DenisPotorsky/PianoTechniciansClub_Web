from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models import (
    Case, CaseTag, CaseMedia, CaseVersion, User,
    Symptom, Tag, Solution, case_symptoms, case_tag_links
)
from app.schemas.case import (
    CaseCreate, CaseUpdate, CaseResponse, CaseListItem,
    SymptomCreate, SymptomResponse,
    TagCreate, TagResponse,
    SolutionCreate, SolutionUpdate, SolutionResponse,
    CaseMediaCreate, CaseMediaResponse,
    CaseVersionResponse,
)
from app.core.security import get_current_user, require_member

router = APIRouter(prefix="/cases", tags=["cases"])


# ===== Вспомогательные функции =====

def build_case_response(case: Case) -> dict:
    """Собирает полный ответ для кейса"""
    return {
        "id": case.id,
        "user_id": case.user_id,
        "author_name": case.author.first_name if case.author else None,
        "title": case.title,
        "description": case.description,
        "symptom_text": case.symptom_text,
        "diagnosis": case.diagnosis,
        "tools_used": case.tools_used,
        "difficulty": case.difficulty,
        "is_verified": case.is_verified,
        "view_count": case.view_count,
        "helpful_count": case.helpful_count,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "symptoms": case.symptoms,
        "tags": case.tags,
        "solutions": [
            {
                "id": s.id,
                "case_id": s.case_id,
                "author_id": s.author_id,
                "author_name": s.author.first_name if s.author else None,
                "text": s.text,
                "tools_used": s.tools_used,
                "difficulty": s.difficulty,
                "is_best": s.is_best,
                "upvotes": s.upvotes,
                "downvotes": s.downvotes,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
            for s in case.solutions
        ],
        "media": case.media,
    }


def build_case_list_item(case: Case) -> dict:
    """Краткая версия для списка"""
    return {
        "id": case.id,
        "title": case.title,
        "symptom_text": case.symptom_text,
        "difficulty": case.difficulty,
        "is_verified": case.is_verified,
        "view_count": case.view_count,
        "helpful_count": case.helpful_count,
        "created_at": case.created_at,
        "author_name": case.author.first_name if case.author else None,
        "symptoms": case.symptoms,
        "tags": case.tags,
        "solutions_count": len(case.solutions),
    }


# ===== CRUD: Кейсы =====

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_case(
    data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_member),
):
    """Создать новый кейс"""
    case = Case(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        symptom_text=data.symptom_text,
        diagnosis=data.diagnosis,
        tools_used=data.tools_used,
        difficulty=data.difficulty,
    )

    # Привязываем симптомы из справочника
    if data.symptom_ids:
        symptoms = db.query(Symptom).filter(Symptom.id.in_(data.symptom_ids)).all()
        case.symptoms = symptoms

    # Привязываем теги из справочника
    if data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
        case.tags = tags

    db.add(case)
    db.flush()

    # Если передано решение — создаём первый Solution
    if data.solution_text:
        solution = Solution(
            case_id=case.id,
            author_id=current_user.id,
            text=data.solution_text,
            tools_used=data.tools_used,
            difficulty=data.difficulty,
            is_best=True,
        )
        db.add(solution)

    db.commit()
    db.refresh(case)
    return build_case_response(case)


@router.get("/")
def list_cases(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = Query(None, description="Поиск по заголовку и описанию"),
    symptom_id: Optional[int] = Query(None, description="Фильтр по симптому"),
    tag_id: Optional[int] = Query(None, description="Фильтр по тегу"),
    difficulty: Optional[str] = Query(None, pattern="^(easy|medium|hard)$"),
    db: Session = Depends(get_db),
):
    """Список кейсов с фильтрацией"""
    query = db.query(Case).options(
        joinedload(Case.author),
        joinedload(Case.symptoms),
        joinedload(Case.tags),
        joinedload(Case.solutions),
    )

    if search:
        query = query.filter(
            Case.title.ilike(f"%{search}%") | Case.symptom_text.ilike(f"%{search}%")
        )
    if symptom_id:
        query = query.filter(Case.symptoms.any(Symptom.id == symptom_id))
    if tag_id:
        query = query.filter(Case.tags.any(Tag.id == tag_id))
    if difficulty:
        query = query.filter(Case.difficulty == difficulty)

    total = query.count()
    cases = query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": [build_case_list_item(c) for c in cases],
    }


@router.get("/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    """Детальная страница кейса"""
    case = db.query(Case).options(
        joinedload(Case.author),
        joinedload(Case.symptoms),
        joinedload(Case.tags),
        joinedload(Case.solutions).joinedload(Solution.author),
        joinedload(Case.media),
    ).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Кейс не найден")

    case.view_count += 1
    db.commit()
    db.refresh(case)

    return build_case_response(case)


@router.put("/{case_id}")
def update_case(
    case_id: int,
    data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить кейс (с сохранением версии)"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Кейс не найден")
    if case.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")

    # Сохраняем текущую версию
    max_version = db.query(func.max(CaseVersion.version)).filter(
        CaseVersion.case_id == case_id
    ).scalar() or 0

    old_version = CaseVersion(
        case_id=case_id,
        version=max_version + 1,
        title=case.title,
        symptom=case.symptom_text or "",
        diagnosis=case.diagnosis,
        solution="",
        tools_used=case.tools_used,
        difficulty=case.difficulty,
        edited_by=current_user.id,
        change_summary=data.change_summary or "Обновление кейса",
    )
    db.add(old_version)

    # Обновляем поля
    if data.title is not None:
        case.title = data.title
    if data.description is not None:
        case.description = data.description
    if data.symptom_text is not None:
        case.symptom_text = data.symptom_text
    if data.diagnosis is not None:
        case.diagnosis = data.diagnosis
    if data.tools_used is not None:
        case.tools_used = data.tools_used
    if data.difficulty is not None:
        case.difficulty = data.difficulty
    if data.symptom_ids is not None:
        symptoms = db.query(Symptom).filter(Symptom.id.in_(data.symptom_ids)).all()
        case.symptoms = symptoms
    if data.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
        case.tags = tags

    db.commit()
    db.refresh(case)
    return build_case_response(case)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить кейс"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Кейс не найден")
    if case.user_id != current_user.id and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Нет прав на удаление")

    db.delete(case)
    db.commit()


# ===== Версии =====

@router.get("/{case_id}/versions", response_model=List[CaseVersionResponse])
def get_case_versions(case_id: int, db: Session = Depends(get_db)):
    """История изменений кейса"""
    versions = db.query(CaseVersion).filter(
        CaseVersion.case_id == case_id
    ).order_by(CaseVersion.version.desc()).all()
    return versions


# ===== Решения (Solutions) =====

@router.post("/{case_id}/solutions", status_code=status.HTTP_201_CREATED)
def add_solution(
    case_id: int,
    data: SolutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_member),
):
    """Добавить решение к кейсу"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Кейс не найден")

    solution = Solution(
        case_id=case_id,
        author_id=current_user.id,
        text=data.text,
        tools_used=data.tools_used,
        difficulty=data.difficulty,
    )
    db.add(solution)
    db.commit()
    db.refresh(solution)

    return {
        "id": solution.id,
        "case_id": solution.case_id,
        "author_id": solution.author_id,
        "author_name": current_user.first_name,
        "text": solution.text,
        "tools_used": solution.tools_used,
        "difficulty": solution.difficulty,
        "is_best": solution.is_best,
        "upvotes": solution.upvotes,
        "downvotes": solution.downvotes,
        "created_at": solution.created_at,
        "updated_at": solution.updated_at,
    }


@router.put("/{case_id}/solutions/{solution_id}")
def update_solution(
    case_id: int,
    solution_id: int,
    data: SolutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить решение"""
    solution = db.query(Solution).filter(
        Solution.id == solution_id, Solution.case_id == case_id
    ).first()
    if not solution:
        raise HTTPException(status_code=404, detail="Решение не найдено")
    if solution.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет прав")

    if data.text is not None:
        solution.text = data.text
    if data.tools_used is not None:
        solution.tools_used = data.tools_used
    if data.difficulty is not None:
        solution.difficulty = data.difficulty
    if data.is_best is not None:
        # Только автор кейса может выбрать лучшее решение
        case = db.query(Case).filter(Case.id == case_id).first()
        if case.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор кейса может выбрать лучшее решение")
        # Сбрасываем is_best у всех решений этого кейса
        db.query(Solution).filter(Solution.case_id == case_id).update({"is_best": False})
        solution.is_best = True

    db.commit()
    db.refresh(solution)
    return {
        "id": solution.id,
        "case_id": solution.case_id,
        "author_id": solution.author_id,
        "text": solution.text,
        "tools_used": solution.tools_used,
        "difficulty": solution.difficulty,
        "is_best": solution.is_best,
        "upvotes": solution.upvotes,
        "downvotes": solution.downvotes,
        "created_at": solution.created_at,
        "updated_at": solution.updated_at,
    }


@router.post("/{case_id}/solutions/{solution_id}/vote")
def vote_solution(
    case_id: int,
    solution_id: int,
    vote: str = Query(..., pattern="^(up|down)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Голосование за решение"""
    solution = db.query(Solution).filter(
        Solution.id == solution_id, Solution.case_id == case_id
    ).first()
    if not solution:
        raise HTTPException(status_code=404, detail="Решение не найдено")

    if vote == "up":
        solution.upvotes += 1
    else:
        solution.downvotes += 1

    db.commit()
    return {"upvotes": solution.upvotes, "downvotes": solution.downvotes}


# ===== Медиа =====

@router.post("/{case_id}/media", status_code=status.HTTP_201_CREATED)
def add_media(
    case_id: int,
    data: CaseMediaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавить фото/видео к кейсу"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Кейс не найден")

    media = CaseMedia(
        case_id=case_id,
        media_type=data.media_type,
        url=data.url,
        description=data.description,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


# ===== Справочник симптомов =====

@router.get("/../symptoms", response_model=List[SymptomResponse])
def list_symptoms(db: Session = Depends(get_db)):
    """Все симптомы"""
    return db.query(Symptom).order_by(Symptom.name).all()

@router.post("/../symptoms", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED)
def create_symptom(
    data: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавить симптом в справочник"""
    existing = db.query(Symptom).filter(Symptom.name.ilike(data.name)).first()
    if existing:
        return existing
    symptom = Symptom(name=data.name, category=data.category, description=data.description)
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    return symptom


# ===== Справочник тегов =====

@router.get("/../tags", response_model=List[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    """Все теги"""
    return db.query(Tag).order_by(Tag.name).all()

@router.post("/../tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавить тег в справочник"""
    existing = db.query(Tag).filter(Tag.name.ilike(data.name)).first()
    if existing:
        return existing
    tag = Tag(name=data.name, category=data.category)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
