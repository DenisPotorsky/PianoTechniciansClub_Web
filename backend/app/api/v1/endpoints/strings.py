from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
import csv
import io

from app.database import get_db
from app.models import User
from app.core.security import require_member, require_admin

router = APIRouter()


class ScaleCreate(BaseModel):
    brand: str
    model: str
    chor_nummer: int
    saiten_im_chor: Optional[int] = None
    laenge_mm: Optional[float] = None
    kern_mm: float
    erste_wicklung_mm: Optional[float] = None
    zweite_wicklung_mm: Optional[float] = None
    typ: Optional[str] = None
    year: Optional[str] = None


class ScaleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    chor_nummer: Optional[int] = None
    saiten_im_chor: Optional[int] = None
    laenge_mm: Optional[float] = None
    kern_mm: Optional[float] = None
    erste_wicklung_mm: Optional[float] = None
    zweite_wicklung_mm: Optional[float] = None
    typ: Optional[str] = None
    year: Optional[str] = None


class ScaleResponse(BaseModel):
    id: int
    brand: str
    model: str
    chor_nummer: int
    saiten_im_chor: Optional[int]
    laenge_mm: Optional[float]
    kern_mm: float
    erste_wicklung_mm: Optional[float]
    zweite_wicklung_mm: Optional[float]
    typ: Optional[str]
    year: Optional[str]


@router.get("/brands")
async def get_brands(
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("SELECT DISTINCT brand FROM scales WHERE brand IS NOT NULL AND brand != '' ORDER BY brand"))
    return [{"brand": row[0]} for row in result.fetchall()]


@router.get("/models/{brand}")
async def get_models(
    brand: str,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("SELECT DISTINCT model FROM scales WHERE LOWER(brand) = LOWER(:brand) AND model IS NOT NULL AND model != '' ORDER BY model"),
        {"brand": brand}
    )
    return [{"model": row[0]} for row in result.fetchall()]


@router.get("/choruses/{brand}/{model}")
async def get_choruses(
    brand: str,
    model: str,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("SELECT DISTINCT chor_nummer FROM scales WHERE LOWER(brand) = LOWER(:brand) AND LOWER(model) = LOWER(:model) AND chor_nummer IS NOT NULL ORDER BY chor_nummer"),
        {"brand": brand, "model": model}
    )
    return [{"chor_nummer": row[0]} for row in result.fetchall()]


@router.get("/data/{brand}/{model}/{chor_nummer}", response_model=List[ScaleResponse])
async def get_string_data(
    brand: str,
    model: str,
    chor_nummer: int,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""SELECT id, brand, model, chor_nummer, saiten_im_chor, laenge_mm, kern_mm,
               erste_wicklung_mm, zweite_wicklung_mm, typ, year
               FROM scales
               WHERE LOWER(brand) = LOWER(:brand) AND LOWER(model) = LOWER(:model) AND chor_nummer = :chor_nummer
               ORDER BY id"""),
        {"brand": brand, "model": model, "chor_nummer": chor_nummer}
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0], "brand": row[1], "model": row[2], "chor_nummer": row[3],
            "saiten_im_chor": row[4], "laenge_mm": row[5], "kern_mm": row[6],
            "erste_wicklung_mm": row[7], "zweite_wicklung_mm": row[8],
            "typ": row[9], "year": row[10]
        }
        for row in rows
    ]


@router.post("/data")
async def create_string_data(
    data: ScaleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    db.execute(
        text("""INSERT INTO scales
                (brand, model, chor_nummer, saiten_im_chor, laenge_mm, kern_mm, erste_wicklung_mm, zweite_wicklung_mm, typ, year)
                VALUES (:brand, :model, :chor_nummer, :saiten_im_chor, :laenge_mm, :kern_mm, :erste_wicklung_mm, :zweite_wicklung_mm, :typ, :year)"""),
        data.model_dump()
    )
    db.commit()
    return {"message": "Запись добавлена"}


@router.put("/data/{record_id}")
async def update_string_data(
    record_id: int,
    data: ScaleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    check = db.execute(text("SELECT id FROM scales WHERE id = :id"), {"id": record_id}).fetchone()
    if not check:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    updates = []
    params = {"id": record_id}
    for field in ["brand", "model", "chor_nummer", "saiten_im_chor", "laenge_mm", "kern_mm", "erste_wicklung_mm", "zweite_wicklung_mm", "typ", "year"]:
        value = getattr(data, field, None)
        if value is not None:
            updates.append(f"{field} = :{field}")
            params[field] = value

    if not updates:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")

    db.execute(text(f"UPDATE scales SET {', '.join(updates)} WHERE id = :id"), params)
    db.commit()
    return {"message": "Запись обновлена"}


@router.delete("/data/{record_id}")
async def delete_string_data(
    record_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    check = db.execute(text("SELECT id FROM scales WHERE id = :id"), {"id": record_id}).fetchone()
    if not check:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.execute(text("DELETE FROM scales WHERE id = :id"), {"id": record_id})
    db.commit()
    return {"message": "Запись удалена"}


@router.post("/import-csv")
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Только CSV файлы")

    content = await file.read()
    text_content = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text_content))

    added = 0
    errors = []

    for row in reader:
        try:
            brand = row.get('brand', '').strip()
            model = row.get('model', '').strip()
            chor_nummer = int(row.get('chor_nummer', 0))
            saiten_im_chor = int(row.get('saiten_im_chor', 0)) if row.get('saiten_im_chor') else None
            laenge_mm = float(row.get('laenge_mm', 0)) if row.get('laenge_mm') else None
            kern_mm = float(row.get('kern_mm', 0))
            erste_wicklung_mm = float(row.get('erste_wicklung_mm', 0)) if row.get('erste_wicklung_mm') else None
            zweite_wicklung_mm = float(row.get('zweite_wicklung_mm', 0)) if row.get('zweite_wicklung_mm') else None
            typ = row.get('typ', '').strip() or None
            year = row.get('year', '').strip() or None

            if not all([brand, model, chor_nummer, kern_mm]):
                errors.append(f"Строка {reader.line_num}: пропущены обязательные поля")
                continue

            db.execute(
                text("""INSERT INTO scales
                        (brand, model, chor_nummer, saiten_im_chor, laenge_mm, kern_mm, erste_wicklung_mm, zweite_wicklung_mm, typ, year)
                        VALUES (:brand, :model, :chor_nummer, :saiten_im_chor, :laenge_mm, :kern_mm, :erste_wicklung_mm, :zweite_wicklung_mm, :typ, :year)"""),
                {"brand": brand, "model": model, "chor_nummer": chor_nummer, "saiten_im_chor": saiten_im_chor,
                 "laenge_mm": laenge_mm, "kern_mm": kern_mm, "erste_wicklung_mm": erste_wicklung_mm,
                 "zweite_wicklung_mm": zweite_wicklung_mm, "typ": typ, "year": year}
            )
            added += 1
        except Exception as e:
            errors.append(f"Строка {reader.line_num}: ошибка - {str(e)}")

    db.commit()
    return {"added": added, "errors": errors[:10]}


@router.get("/export-csv")
async def export_csv(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    result = db.execute(text(
        "SELECT id, brand, model, chor_nummer, saiten_im_chor, laenge_mm, kern_mm, erste_wicklung_mm, zweite_wicklung_mm, typ, year FROM scales ORDER BY brand, model, chor_nummer"))
    rows = result.fetchall()

    columns = ['id', 'brand', 'model', 'chor_nummer', 'saiten_im_chor', 'laenge_mm', 'kern_mm', 'erste_wicklung_mm', 'zweite_wicklung_mm', 'typ', 'year']

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=strings_data.csv"}
    )
