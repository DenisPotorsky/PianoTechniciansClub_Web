import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from datetime import datetime, timedelta
import secrets

from app.core.security import create_access_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email-писем"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)

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

            # HTML-версия письма
            msg.attach(MIMEText(html_content, "html"))

            # Отправка
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Письмо отправлено на {to_email}")
            return True

        except Exception as e:
            logger.error(f"Ошибка отправки письма: {e}")
            return False

    def generate_token(self) -> str:
        """Сгенерировать уникальный токен"""
        return secrets.token_urlsafe(32)

    def send_verification_email(self, email: str, username: str, token: str) -> bool:
        """Отправить письмо с подтверждением регистрации"""
        verification_url = f"{self.frontend_url}/verify-email?token={token}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 2px solid #4f46e5; padding-bottom: 20px; }}
                .header h1 {{ color: #4f46e5; font-size: 28px; }}
                .content {{ padding: 20px 0; }}
                .btn {{ display: inline-block; background: #4f46e5; color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎹 PianoTechniciansClub</h1>
                </div>
                <div class="content">
                    <h2>Добро пожаловать, {username}!</h2>
                    <p>Благодарим за регистрацию в закрытом клубе фортепианных мастеров.</p>
                    <p>Для завершения регистрации и подтверждения email-адреса нажмите на кнопку ниже:</p>
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="btn">Подтвердить email</a>
                    </div>
                    <p style="color: #888; font-size: 14px;">Ссылка действительна в течение 24 часов.</p>
                    <p style="color: #888; font-size: 14px;">Если вы не регистрировались на PianoTechniciansClub, просто проигнорируйте это письмо.</p>
                </div>
                <div class="footer">
                    <p>© 2026 PianoTechniciansClub. Все права защищены.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self._send_email(email, "Подтверждение регистрации в PianoTechniciansClub", html)

    def send_password_reset_email(self, email: str, username: str, token: str) -> bool:
        """Отправить письмо для сброса пароля"""
        reset_url = f"{self.frontend_url}/reset-password?token={token}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 2px solid #ef4444; padding-bottom: 20px; }}
                .header h1 {{ color: #ef4444; font-size: 28px; }}
                .content {{ padding: 20px 0; }}
                .btn {{ display: inline-block; background: #ef4444; color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔑 Восстановление пароля</h1>
                </div>
                <div class="content">
                    <h2>Здравствуйте, {username}!</h2>
                    <p>Вы запросили сброс пароля для аккаунта в PianoTechniciansClub.</p>
                    <p>Для создания нового пароля нажмите на кнопку ниже:</p>
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="btn">Сбросить пароль</a>
                    </div>
                    <p style="color: #888; font-size: 14px;">Ссылка действительна в течение 24 часов.</p>
                    <p style="color: #888; font-size: 14px;">Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
                </div>
                <div class="footer">
                    <p>© 2026 PianoTechniciansClub. Все права защищены.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self._send_email(email, "Сброс пароля в PianoTechniciansClub", html)

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

            # Для Яндекс.Почты с портом 465 (SSL)
            if self.smtp_port == 465:
                import ssl
                # Создаём контекст без проверки сертификата (для macOS)
                context = ssl._create_unverified_context()
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())
            else:
                # STARTTLS (порт 587)
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Письмо отправлено на {to_email}")
            return True

        except Exception as e:
            logger.error(f"Ошибка отправки письма: {e}")
            return False