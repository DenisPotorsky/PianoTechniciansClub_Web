from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import config

# Создаем движок. check_same_thread=False важен для SQLite в async окружении
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Генератор сессии для Dependency Injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()