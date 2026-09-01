import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

try:
    server = smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT")))
    server.starttls()
    server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
    print("✅ Аутентификация успешна!")

    # === ОТПРАВКА ПИСЬМА ===
    msg = MIMEMultipart()
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"] = os.getenv("ADMIN_EMAIL")
    msg["Subject"] = "Тестовое письмо"
    body = "Привет! Это тестовое письмо."
    msg.attach(MIMEText(body, "plain"))

    server.sendmail(os.getenv("SMTP_USER"), os.getenv("ADMIN_EMAIL"), msg.as_string())
    print("✅ Письмо отправлено!")

    server.quit()
except Exception as e:
    print(f"❌ Ошибка: {e}")