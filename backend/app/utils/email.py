import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

ADMIN_NAME = "Denis"
ADMIN_EMAIL = "denis-s2@yandex.ru"


def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """Отправить email"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email

        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)

        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())

        logger.info(f"✅ Email отправлен на {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email: {e}")
        return False


def send_access_confirmation_email(email: str, full_name: str, password: str, user_id: int):
    """Отправить письмо с подтверждением доступа"""
    subject = "🎹 Доступ в PianoTechniciansClub подтверждён!"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: #1e3a5f; text-align: center; }}
            .info {{ background: #f0f7ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .password {{ background: #e8f5e9; padding: 12px; border-radius: 6px; font-size: 18px; text-align: center; font-weight: bold; color: #2e7d32; }}
            .btn {{ display: inline-block; background: #1e3a5f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎹 PianoTechniciansClub</h1>
            <p>Здравствуйте, <strong>{full_name}</strong>!</p>
            <p>Ваш доступ в закрытый клуб фортепианных мастеров <strong>подтверждён</strong>! ✅</p>

            <div class="info">
                <p><strong>Ваши данные для входа:</strong></p>
                <p>📧 <strong>Email:</strong> {email}</p>
                <p>🔑 <strong>Пароль:</strong></p>
                <div class="password">{password}</div>
                <p style="font-size: 14px; color: #666; margin-top: 10px;">
                    ⚠️ <strong>Рекомендуем сменить пароль</strong> после первого входа в профиле.
                </p>
            </div>

            <p style="text-align: center;">
                <a href="{settings.APP_URL}/login" class="btn">🔓 Войти в клуб</a>
            </p>

            <p style="color: #555; font-size: 14px;">
                Добро пожаловать в сообщество профессионалов! 🎹
            </p>

            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #999; font-size: 12px; text-align: center;">
                По всем вопросам: <a href="mailto:{ADMIN_EMAIL}">{ADMIN_EMAIL}</a>
            </p>

            <div class="footer">
                <p>PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса</p>
                <p>Это письмо отправлено автоматически, отвечать на него не нужно.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    PianoTechniciansClub - Доступ подтверждён!

    Здравствуйте, {full_name}!

    Ваш доступ в закрытый клуб фортепианных мастеров подтверждён! ✅

    Ваши данные для входа:
    Email: {email}
    Пароль: {password}

    Рекомендуем сменить пароль после первого входа.

    Войдите в клуб: {settings.APP_URL}/login

    Добро пожаловать в сообщество профессионалов! 🎹

    ---
    По всем вопросам: {ADMIN_EMAIL}
    PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса
    """

    return send_email(email, subject, html_content, text_content)


def send_access_rejected_email(email: str, full_name: str):
    """Отправить письмо об отклонении доступа"""
    subject = "❌ Доступ в PianoTechniciansClub отклонён"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: #c62828; text-align: center; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>❌ PianoTechniciansClub</h1>
            <p>Здравствуйте, <strong>{full_name}</strong>!</p>
            <p>К сожалению, ваша заявка на доступ в закрытый клуб фортепианных мастеров <strong>отклонена</strong>.</p>
            <p>Если вы считаете, что это ошибка, свяжитесь с администратором.</p>

            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #999; font-size: 12px; text-align: center;">
                По всем вопросам: <a href="mailto:{ADMIN_EMAIL}">{ADMIN_EMAIL}</a>
            </p>

            <div class="footer">
                <p>PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    PianoTechniciansClub - Доступ отклонён

    Здравствуйте, {full_name}!

    К сожалению, ваша заявка на доступ в закрытый клуб фортепианных мастеров отклонена.

    Если вы считаете, что это ошибка, свяжитесь с администратором: {ADMIN_EMAIL}

    ---
    PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса
    """

    return send_email(email, subject, html_content, text_content)


def send_whitelist_added_email(email: str, full_name: str):
    """Отправить письмо о добавлении в белый список"""
    subject = "👑 Вы добавлены в белый список PianoTechniciansClub"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: #f57c00; text-align: center; }}
            .btn {{ display: inline-block; background: #f57c00; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👑 PianoTechniciansClub</h1>
            <p>Здравствуйте, <strong>{full_name}</strong>!</p>
            <p>Вы добавлены в <strong>белый список</strong> клуба! 🎉</p>
            <p>Теперь вы можете входить в клуб <strong>без пароля</strong> по Telegram ID.</p>

            <p style="text-align: center;">
                <a href="{settings.APP_URL}/whitelist-login" class="btn">👑 Войти по Telegram ID</a>
            </p>

            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #999; font-size: 12px; text-align: center;">
                По всем вопросам: <a href="mailto:{ADMIN_EMAIL}">{ADMIN_EMAIL}</a>
            </p>

            <div class="footer">
                <p>PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    PianoTechniciansClub - Вы добавлены в белый список!

    Здравствуйте, {full_name}!

    Вы добавлены в белый список клуба! 🎉

    Теперь вы можете входить в клуб без пароля по Telegram ID.

    Войдите: {settings.APP_URL}/whitelist-login

    ---
    По всем вопросам: {ADMIN_EMAIL}
    PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса
    """

    return send_email(email, subject, html_content, text_content)


# ============ НОВЫЕ ФУНКЦИИ ============

def send_admin_notification_about_request(email: str, full_name: str, request_id: int, message: str = None):
    """Уведомление админу о новой заявке на доступ"""
    subject = "📩 Новая заявка на доступ в PianoTechniciansClub"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: #1e3a5f; text-align: center; }}
            .info {{ background: #fff8e1; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff9800; }}
            .btn {{ display: inline-block; background: #1e3a5f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📩 PianoTechniciansClub</h1>
            <p>Здравствуйте, администратор!</p>
            <p>Поступила <strong>новая заявка на доступ</strong> в клуб.</p>

            <div class="info">
                <p><strong>👤 Пользователь:</strong> {full_name}</p>
                <p><strong>📧 Email:</strong> {email}</p>
                <p><strong>📝 Сообщение:</strong> {message or 'Не указано'}</p>
                <p><strong>🆔 ID заявки:</strong> {request_id}</p>
            </div>

            <p style="text-align: center;">
                <a href="{settings.APP_URL}/admin" class="btn">👑 Перейти в админ-панель</a>
            </p>

            <div class="footer">
                <p>PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса</p>
                <p>Это письмо отправлено автоматически.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    PianoTechniciansClub - Новая заявка на доступ!

    Здравствуйте, администратор!

    Поступила новая заявка на доступ в клуб.

    Пользователь: {full_name}
    Email: {email}
    Сообщение: {message or 'Не указано'}
    ID заявки: {request_id}

    Перейдите в админ-панель для обработки: {settings.APP_URL}/admin

    ---
    PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса
    """

    return send_email(email, subject, html_content, text_content)


def send_user_status_changed_email(email: str, full_name: str, status: str):
    """Уведомление пользователю об изменении статуса подписки"""
    if status == "approved":
        subject = "✅ Ваш доступ в PianoTechniciansClub подтверждён!"
        title = "Доступ подтверждён! ✅"
        message = "Ваш доступ в закрытый клуб фортепианных мастеров подтверждён. Добро пожаловать! 🎹"
        color = "#4caf50"
    elif status == "rejected":
        subject = "❌ Ваш доступ в PianoTechniciansClub отклонён"
        title = "Доступ отклонён ❌"
        message = "К сожалению, ваш доступ в клуб был отклонён администратором."
        color = "#f44336"
    else:
        subject = "🔄 Статус доступа в PianoTechniciansClub изменён"
        title = "Статус изменён"
        message = f"Ваш статус доступа изменён на: {status}"
        color = "#ff9800"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: {color}; text-align: center; }}
            .info {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .btn {{ display: inline-block; background: #1e3a5f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            <p>Здравствуйте, <strong>{full_name}</strong>!</p>
            <p>{message}</p>
            <p style="text-align: center;">
                <a href="{settings.APP_URL}/profile" class="btn">👤 Перейти в профиль</a>
            </p>
            <div class="footer">
                <p>PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса</p>
                <p>По всем вопросам: <a href="mailto:{ADMIN_EMAIL}">{ADMIN_EMAIL}</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    PianoTechniciansClub - {title}

    Здравствуйте, {full_name}!

    {message}

    Перейдите в профиль: {settings.APP_URL}/profile

    ---
    По всем вопросам: {ADMIN_EMAIL}
    PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса
    """

    return send_email(email, subject, html_content, text_content)


def send_new_user_notification_to_admin(user_data: dict):
    """Уведомление админу о новом зарегистрированном пользователе"""
    subject = "👤 Новый пользователь в PianoTechniciansClub"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            h1 {{ color: #1e3a5f; text-align: center; }}
            .info {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }}
            .btn {{ display: inline-block; background: #1e3a5f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👤 PianoTechniciansClub</h1>
            <p>Здравствуйте, администратор!</p>
            <p>Зарегистрировался <strong>новый пользователь</strong>.</p>

            <div class="info">
                <p><strong>👤 Имя:</strong> {user_data.get('first_name')} {user_data.get('last_name', '')}</p>
                <p><strong>📧 Email:</strong> {user_data.get('email')}</p>
                <p><strong>🆔 Telegram ID:</strong> {user_data.get('telegram_id')}</p>
                <p><strong>📅 Дата регистрации:</strong> {user_data.get('created_at')}</p>
            </div>

            <p style="text-align: center;">
                <a href="{settings.APP_URL}/admin" class="btn">👑 Перейти в админ-панель</a>
            </p>

            <div class="footer">
                <p>PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса</p>
                <p>Это письмо отправлено автоматически.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    PianoTechniciansClub - Новый пользователь!

    Здравствуйте, администратор!

    Зарегистрировался новый пользователь:
    Имя: {user_data.get('first_name')} {user_data.get('last_name', '')}
    Email: {user_data.get('email')}
    Telegram ID: {user_data.get('telegram_id')}

    Перейдите в админ-панель: {settings.APP_URL}/admin

    ---
    PianoTechniciansClub — закрытый клуб фортепианных мастеров экстра-класса
    """

    return send_email(ADMIN_EMAIL, subject, html_content, text_content)


def send_test_email():
    """Отправить тестовое письмо"""
    to_email = "denis-s2@yandex.ru"
    subject = "🧪 Тестовое письмо от PianoTechniciansClub"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #f8f9fa; border-radius: 12px; padding: 30px; }}
            h1 {{ color: #1e3a5f; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎹 PianoTechniciansClub</h1>
            <p>✅ Это тестовое письмо!</p>
            <p>Ваша почта настроена правильно и работает.</p>
            <p>— <strong>Denis</strong>, администратор</p>
        </div>
    </body>
    </html>
    """

    text_content = "🎹 PianoTechniciansClub\n\nЭто тестовое письмо!\nВаша почта настроена правильно и работает."

    return send_email(to_email, subject, html_content, text_content)