import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.yandex.ru")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.frontend_url = os.getenv("APP_URL", "http://localhost:3000")
        self.from_email = os.getenv("SMTP_FROM", self.smtp_user)

    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
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
        verification_url = f"{self.frontend_url}/verify-email?token={token}"
        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <h2>Добро пожаловать в PianoTechniciansClub!</h2>
            <p>Для подтверждения email перейдите по ссылке:</p>
            <a href="{verification_url}" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:8px;">Подтвердить email</a>
            <p style="color:#999;font-size:12px;margin-top:20px;">Ссылка действует 24 часа.</p>
        </body></html>"""
        return self._send_email(email, "Подтверждение регистрации — PianoTechniciansClub", html)

    def send_password_reset_email(self, email: str, username: str, token: str) -> bool:
        reset_url = f"{self.frontend_url}/reset-password?token={token}"
        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <h2>Сброс пароля</h2>
            <p>Здравствуйте, {username}!</p>
            <p>Вы запросили сброс пароля в PianoTechniciansClub.</p>
            <a href="{reset_url}" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:8px;">Сбросить пароль</a>
            <p style="color:#999;font-size:12px;margin-top:20px;">Ссылка действует 1 час. Если вы не запрашивали сброс — проигнорируйте это письмо.</p>
        </body></html>"""
        return self._send_email(email, "Сброс пароля — PianoTechniciansClub", html)

    def send_welcome_email(self, email: str, username: str) -> bool:
        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <h2>Добро пожаловать, {username}!</h2>
            <p>Ваш email подтверждён. Теперь у вас есть полный доступ к PianoTechniciansClub.</p>
            <ul><li>Калькулятор басовых струн</li><li>Атлас возрастов фортепиано</li><li>База мензур</li><li>Регулировочные параметры</li></ul>
            <a href="{self.frontend_url}" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:8px;">Перейти на сайт</a>
        </body></html>"""
        return self._send_email(email, "Добро пожаловать в PianoTechniciansClub!", html)

    def send_approval_email(self, email: str, full_name: str, temp_password: str) -> bool:
        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <h2>Заявка одобрена!</h2>
            <p>Здравствуйте, {full_name}!</p>
            <p>Ваша заявка на вступление в <b>PianoTechniciansClub</b> одобрена.</p>
            <p>Ваши данные для входа:</p>
            <table style="border-collapse:collapse;margin:16px 0;">
                <tr><td style="padding:8px;border:1px solid #ddd;"><b>Email:</b></td><td style="padding:8px;border:1px solid #ddd;">{email}</td></tr>
                <tr><td style="padding:8px;border:1px solid #ddd;"><b>Пароль:</b></td><td style="padding:8px;border:1px solid #ddd;"><code>{temp_password}</code></td></tr>
            </table>
            <p>Рекомендуем сменить пароль после первого входа.</p>
            <a href="{self.frontend_url}/login" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:8px;">Войти на сайт</a>
        </body></html>"""
        return self._send_email(email, "Заявка одобрена — PianoTechniciansClub", html)

    def send_rejection_email(self, email: str, full_name: str) -> bool:
        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <h2>Заявка отклонена</h2>
            <p>Здравствуйте, {full_name}!</p>
            <p>К сожалению, ваша заявка на вступление в PianoTechniciansClub не была одобрена.</p>
            <p>Если вы считаете это ошибкой, свяжитесь с администрацией.</p>
        </body></html>"""
        return self._send_email(email, "Заявка отклонена — PianoTechniciansClub", html)

    def send_new_request_notification(self, email: str, full_name: str, message: str = None) -> bool:
        admin_email = os.getenv("ADMIN_EMAIL")
        if not admin_email:
            logger.warning("ADMIN_EMAIL не настроен в .env")
            return False
        subject = "Новая заявка на доступ — PianoTechniciansClub"
        html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <h2>Новая заявка на доступ</h2>
            <table style="border-collapse:collapse;margin:16px 0;">
                <tr><td style="padding:8px;border:1px solid #ddd;"><b>ФИО:</b></td><td style="padding:8px;border:1px solid #ddd;">{full_name}</td></tr>
                <tr><td style="padding:8px;border:1px solid #ddd;"><b>Email:</b></td><td style="padding:8px;border:1px solid #ddd;">{email}</td></tr>
                <tr><td style="padding:8px;border:1px solid #ddd;"><b>Сообщение:</b></td><td style="padding:8px;border:1px solid #ddd;">{message or '—'}</td></tr>
            </table>
            <a href="{self.frontend_url}/admin" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:8px;">Перейти в админку</a>
        </body></html>"""
        return self._send_email(admin_email, subject, html)
