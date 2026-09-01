from app.database import SessionLocal
from app.models import User

db = SessionLocal()

users_data = [
    {'telegram_id': 474982734, 'first_name': 'Энестейша', 'last_name': 'Admin'},
    {'telegram_id': 274243165, 'first_name': 'Лёхич', 'last_name': 'Admin'},
]

for data in users_data:
    existing = db.query(User).filter(User.telegram_id == data['telegram_id']).first()
    if existing:
        existing.is_subscribed = True
        existing.is_admin = True
        existing.first_name = data['first_name']
        existing.last_name = data['last_name']
        print(f'✅ Пользователь {data["telegram_id"]} обновлён')
    else:
        new_user = User(
            telegram_id=data['telegram_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=f"admin_{data['telegram_id']}",
            is_subscribed=True,
            is_admin=True,
            is_super_admin=False,
            is_active=True
        )
        db.add(new_user)
        print(f'✅ Пользователь {data["telegram_id"]} создан')

db.commit()
db.close()
print('✅ Все пользователи добавлены в белый список!')