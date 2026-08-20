"""
Импорт регулировочных параметров из CSV (Карл-Йохан Форсс, 2009).

Источник: «Регулировка механики пианино и роялей», таблицы стр. 300–311.
Данные оцифрованы со сканов; значения со звёздочкой (*) — сноска в книге.

Запуск из каталога backend:
    python import_forss_regulating.py
    python import_forss_regulating.py --replace
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from app.database import SessionLocal, engine
from app.models import Base, RegulatingParam

CSV_PATH = Path(__file__).parent / "data" / "forss_regulating.csv"
SOURCE_BRANDS = {
    "Baldwin",
    "Bechstein",
    "Blüthner",
    "Bösendorfer",
    "Fazioli",
    "Aug. Förster",
    "Grotrian-Steinweg",
    "Rud. Ibach",
    "Kimball",
    "Petrof",
    "Sauter",
    "Schimmel",
    "Seiler",
    "Samick",
    "Steinway & Sons",
    "Yamaha",
}


def import_rows(*, replace: bool = False) -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV не найден: {CSV_PATH}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if replace:
            deleted = (
                db.query(RegulatingParam)
                .filter(RegulatingParam.brand.in_(SOURCE_BRANDS))
                .delete(synchronize_session=False)
            )
            db.commit()
            print(f"Удалено старых записей Forss: {deleted}")

        added = 0
        skipped = 0

        with CSV_PATH.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                brand = (row.get("brand") or "").strip()
                model = (row.get("model") or "").strip()
                parameter = (row.get("parameter") or "").strip()
                value = (row.get("value") or "").strip()
                unit = (row.get("unit") or "").strip() or None

                if not all([brand, model, parameter, value]):
                    skipped += 1
                    continue

                exists = (
                    db.query(RegulatingParam)
                    .filter(
                        RegulatingParam.brand == brand,
                        RegulatingParam.model == model,
                        RegulatingParam.parameter == parameter,
                        RegulatingParam.value == value,
                    )
                    .first()
                )
                if exists:
                    skipped += 1
                    continue

                db.add(
                    RegulatingParam(
                        brand=brand,
                        model=model,
                        parameter=parameter,
                        value=value,
                        unit=unit,
                    )
                )
                added += 1

        db.commit()
        total = db.query(RegulatingParam).count()
        print(f"Добавлено: {added}")
        print(f"Пропущено (дубликаты/пустые): {skipped}")
        print(f"Всего в regulating_params: {total}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Импорт параметров Forss")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Удалить ранее импортированные бренды Forss перед загрузкой",
    )
    args = parser.parse_args()
    import_rows(replace=args.replace)
