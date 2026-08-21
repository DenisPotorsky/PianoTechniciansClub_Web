import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Импортируем наш email-сервис
from app.services.email_service import EmailService


def send_test_email():
    """Отправить тестовое письмо на указанный email"""

    # Берём email из .env или вводим вручную
    test_email = os.getenv("TEST_EMAIL", "your_email@gmail.com")

    if not test_email or test_email == "your_email@gmail.com":
        print("❌ Укажите TEST_EMAIL в файле .env или измените код")
        print("📝 Например: TEST_EMAIL=your_email@gmail.com")
        return False

    print(f"📧 Отправка тестового письма на {test_email}...")

    email_service = EmailService()

    # Отправляем тестовое письмо
    result = email_service.send_verification_email(
        email=test_email,
        username="Тестовый пользователь",
        token="test_token_123"
    )

    if result:
        print("✅ Письмо успешно отправлено!")
        print("📬 Проверьте почту (возможно, письмо в папке Спам)")
        return True
    else:
        print("❌ Ошибка отправки письма")
        print("\n🔍 Проверьте настройки в файле .env:")
        print("  SMTP_HOST=", os.getenv("SMTP_HOST"))
        print("  SMTP_PORT=", os.getenv("SMTP_PORT"))
        print("  SMTP_USER=", os.getenv("SMTP_USER"))
        print("  SMTP_PASSWORD=", "****" if os.getenv("SMTP_PASSWORD") else "❌ НЕ УСТАНОВЛЕН")
        print("  FROM_EMAIL=", os.getenv("FROM_EMAIL"))
        return False


if __name__ == "__main__":
    result = send_test_email()
    if result:
        print("\n✅ Письмо отправлено! Проверьте почту.")
    else:
        print("\n❌ Ошибка отправки. Проверьте настройки .env")