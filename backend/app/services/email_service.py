import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email-писем"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.yandex.ru")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.frontend_url = os.getenv("APP_URL", "http://localhost:3000")
        self.from_email = os.getenv("SMTP_FROM", self.smtp_user)

    def generate_token(self) -> str:
        """Сгенерировать уникальный токен"""
        return secrets.token_urlsafe(32)

    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Отправить email"""
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.warning("SMTP не настроен. Письмо не отправлено.")
                return False

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            msg.attach(MIMEText(html_content, "html"))

            if self.smtp_port == 465:
                import ssl
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Письмо отправлено на {to_email}")
            return True

        except Exception as e:
            logger.error(f"Ошибка отправки письма: {e}")
            return False

    def send_verification_email(self, email: str, username: str, token: str) -> bool:
        """Отправить письмо с подтверждением регистрации"""
        verification_url = f"{self.frontend_url}/verify-email?token={token}"

        html = f"""
        <html>
        <body>
            <h2>Добро пожаловать в PianoTechniciansClub!</h2>
            <p>Для подтверждения email перейдите по ссылке:</p>
            <a href="{verification_url}">Подтвердить email</a>
        </body>
        </html>
        """
        return self._send_email(email, "Подтверждение регистрации", html)

    def send_password_reset_email(self, email: str, username: str, token: str) -> bool:
        """Отправить письмо для сброса пароля"""
        reset_url = f"{self.frontend_url}/reset-password?token={token}"

        html = f"""
        <html>
        <body>
            <h2>Сброс пароля</h2>
            <p>Для сброса пароля перейдите по ссылке:</p>
            <a href="{reset_url}">Сбросить пароль</a>
        </body>
        </html>
        """
        return self._send_email(email, "Сброс пароля", html)

    def send_welcome_email(self, email: str, username: str) -> bool:
        """Отправить приветственное письмо"""
        html = f"""
        <html>
        <body>
            <h2>Добро пожаловать в PianoTechniciansClub!</h2>
            <p>Ваш email подтверждён. Теперь вы можете войти в систему.</p>
        </body>
        </html>
        """
        return self._send_email(email, "Добро пожаловать!", html)

    def send_new_request_notification(self, email: str, full_name: str, message: str = None) -> bool:
        """Отправить уведомление админу о новой заявке"""
        admin_email = os.getenv("ADMIN_EMAIL")
        if not admin_email:
            print("❌ ADMIN_EMAIL не настроен в .env")
            return False

        subject = "📩 Новая заявка на доступ в PianoTechniciansClub"
        html = f"""
        <html>
        <body>
            <h2>📩 Новая заявка на доступ</h2>
            <p><b>ФИО:</b> {full_name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Сообщение:</b> {message or '—'}</p>
            <br>
            <a href="{self.frontend_url}/admin">Перейти в админку →</a>
        </body>
        </html>
        """
        return self._send_email(admin_email, subject, html)