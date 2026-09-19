from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://piano:piano@db:5432/piano_club")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
