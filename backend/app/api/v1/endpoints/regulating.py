from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import csv
import io

from app.database import get_db
from app.models import RegulatingParam, User
from app.core.security import require_admin, require_member

router = APIRouter()


@router.get("/")
async def get_params(
        search: Optional[str] = None,
        brand: Optional[str] = None,
        limit: int = 100,
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    query = db.query(RegulatingParam)
    all_params = query.all()

    if brand:
        all_params = [p for p in all_params if p.brand.lower() == brand.lower()]

    if search:
        search_lower = search.lower()
        all_params = [
            r for r in all_params
            if search_lower in r.brand.lower()
            or search_lower in r.model.lower()
            or search_lower in r.parameter.lower()
        ]

    all_params = sorted(all_params, key=lambda x: (x.brand, x.model))[:limit]

    return [{
        "id": r.id,
        "brand": r.brand,
        "model": r.model,
        "parameter": r.parameter,
        "value": r.value,
        "unit": r.unit
    } for r in all_params]


@router.get("/brands")
async def get_brands(
        current_user: User = Depends(require_member),
        db: Session = Depends(get_db)
):
    brands = db.query(RegulatingParam.brand).distinct().order_by(RegulatingParam.brand).all()
    return [b[0] for b in brands if b[0]]


@router.post("/")
async def create_param(
        brand: str,
        model: str,
        parameter: str,
        value: str,
        unit: Optional[str] = None,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    new_param = RegulatingParam(
        brand=brand,
        model=model,
        parameter=parameter,
        value=value,
        unit=unit
    )
    db.add(new_param)
    db.commit()
    db.refresh(new_param)
    return {"message": "Параметр добавлен", "id": new_param.id}


@router.delete("/{param_id}")
async def delete_param(
        param_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    param = db.query(RegulatingParam).filter(RegulatingParam.id == param_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="Параметр не найден")

    db.delete(param)
    db.commit()
    return {"message": "Параметр удалён"}


@router.post("/import-csv")
async def import_csv(
        file: UploadFile = File(...),
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Нужен файл .csv")

    content = await file.read()
    text = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))

    added = 0
    errors = []

    existing_params = db.query(RegulatingParam).all()

    for row in reader:
        try:
            brand = row.get('brand', '').strip()
            model = row.get('model', '').strip()
            parameter = row.get('parameter', '').strip()
            value = row.get('value', '').strip()
            unit = row.get('unit', '').strip() or None

            if not all([brand, model, parameter, value]):
                errors.append(f"Пропущены поля в строке: {row}")
                continue

            existing = None
            for p in existing_params:
                if (p.brand.lower() == brand.lower() and
                        p.model.lower() == model.lower() and
                        p.parameter.lower() == parameter.lower()):
                    existing = p
                    break

            if existing:
                errors.append(f"Дубликат: {brand} {model} {parameter}")
                continue

            new_param = RegulatingParam(
                brand=brand,
                model=model,
                parameter=parameter,
                value=value,
                unit=unit
            )
            db.add(new_param)
            existing_params.append(new_param)
            added += 1

        except Exception as e:
            errors.append(f"Ошибка: {str(e)}")

    db.commit()

    return {
        "added": added,
        "errors": errors[:10]
    }