import os
from dotenv import load_dotenv
from app.services.email_service import EmailService

load_dotenv()

email_service = EmailService()
result = email_service._send_email(
    to_email="denis-s2@yandex.ru",
    subject="Тестовое письмо",
    html_content="<h1>Привет!</h1><p>Это тест.</p>"
)
print("Результат:", result)