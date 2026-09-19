from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import config

# Создаем движок для PostgreSQL
connect_args = {}
if "sqlite" in config.DATABASE_URL:
    connect_args["check_same_thread"] = False
engine = create_engine(config.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Генератор сессии для Dependency Injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()