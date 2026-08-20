from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

AGE_DATABASE_URL = "sqlite:///./piano_age.db"

age_engine = create_engine(
    AGE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

AgeSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=age_engine)

def get_age_db():
    db = AgeSessionLocal()
    try:
        yield db
    finally:
        db.close()