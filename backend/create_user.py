import asyncio
from app.database import AsyncSessionLocal
from app.services.user_service import UserService


async def create_test_user():
    async with AsyncSessionLocal() as session:
        user_service = UserService(session)

        user = await user_service.get_or_create_user(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User"
        )

        print(f"✅ Пользователь создан:")
        print(f"   ID: {user.id}")
        print(f"   Telegram ID: {user.telegram_id}")
        print(f"   Имя: {user.first_name} {user.last_name}")
        print(f"   Username: {user.username}")

        return user.id


if __name__ == "__main__":
    user_id = asyncio.run(create_test_user())
    print(f"\n📝 Используйте этот ID для тестов: {user_id}")