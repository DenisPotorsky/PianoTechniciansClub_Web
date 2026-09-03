from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.endpoints import router
from app.config import get_settings
from app.database import engine, Base, SessionLocal
from app.models import User, Brand, SerialRange, Scale, RegulatingParam, Calculation
import json
import os
from datetime import datetime

settings = get_settings()

def parse_dt(v):
    if v is None: return None
    if isinstance(v, datetime): return v
    try: return datetime.fromisoformat(str(v))
    except: return None

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Импорт данных из JSON если таблицы пустые
    export_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "all_data_export.json")
    users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users_export.json")

    if db.query(Brand).count() == 0 and os.path.exists(export_file):
        with open(export_file, "r") as f:
            data = json.load(f)

        for item in data.get("brands", []):
            db.add(Brand(id=item["id"], name=item.get("name"), country=item.get("country"), info=item.get("info"), type=item.get("type")))

        for item in data.get("serial_ranges", []):
            db.add(SerialRange(id=item["id"], brand_id=item.get("brand_id"), serial_start=item.get("serial_start"), serial_end=item.get("serial_end"), year=item.get("year")))

        scale_cols = ["id","brand","model","chor_nummer","saiten_im_chor","laenge_mm","kern_mm","erste_wicklung_mm","zweite_wicklung_mm","typ","year"]
        for item in data.get("scales", []):
            d = {k: item.get(k) for k in scale_cols}
            d["created_at"] = parse_dt(item.get("created_at"))
            d["updated_at"] = parse_dt(item.get("updated_at"))
            db.add(Scale(**d))

        rp_cols = ["id","brand","model","parameter","value","unit"]
        for item in data.get("regulating_params", []):
            d = {k: item.get(k) for k in rp_cols}
            d["created_at"] = parse_dt(item.get("created_at"))
            d["updated_at"] = parse_dt(item.get("updated_at"))
            db.add(RegulatingParam(**d))

        calc_cols = ["id","user_id","winding_type","core_diameter","total_diameter","string_length","result_data","is_favorite"]
        for item in data.get("calculations", []):
            d = {k: item.get(k) for k in calc_cols}
            d["created_at"] = parse_dt(item.get("created_at"))
            db.add(Calculation(**d))

        db.commit()
        print(f"✅ Данные импортированы: brands={db.query(Brand).count()}, scales={db.query(Scale).count()}")

    # Импорт пользователей
    if db.query(User).count() == 0 and os.path.exists(users_file):
        with open(users_file, "r") as f:
            users_data = json.load(f)
        for u in users_data:
            db.add(User(
                telegram_id=u["telegram_id"],
                username=u.get("username"),
                first_name=u.get("first_name") or u.get("username") or "User",
                last_name=u.get("last_name"),
                email=u.get("email"),
                phone=u.get("phone"),
                city=u.get("city"),
                hashed_password=u.get("hashed_password"),
                is_subscribed=bool(u.get("is_subscribed")),
                is_approved=bool(u.get("is_approved")),
                is_admin=bool(u.get("is_admin")),
                is_super_admin=bool(u.get("is_super_admin")),
                is_active=bool(u.get("is_active"))
            ))
        db.commit()
        print(f"✅ Пользователи импортированы: {db.query(User).count()}")

    db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="PianoTechniciansClub API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "PianoTechniciansClub API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
