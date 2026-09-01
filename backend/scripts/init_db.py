from app.database import engine
from app.models import Base

def init_database():
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована!")
    print("📋 Созданы таблицы: users, brands, serial_ranges, calculations, access_requests, notifications, regulating_params")

if __name__ == "__main__":
    init_database()