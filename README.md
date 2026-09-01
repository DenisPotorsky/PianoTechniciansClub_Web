# 🎹 PianoTechniciansClub

Закрытый клуб для профессиональных фортепианных мастеров.

## 📦 Состав проекта

| Компонент | Папка | Стек |
|-----------|-------|------|
| Веб-сайт | frontend/ | React 19 + TypeScript + TailwindCSS |
| API-сервер | backend/ | FastAPI + SQLAlchemy + SQLite |
| Telegram-бот | bot_simple/ | python-telegram-bot |

## 🚀 Быстрый старт

### Backend
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

### Frontend
    cd frontend
    npm install
    npm start

### Telegram-бот
    cd bot_simple
    cp .env.example .env
    python main.py

## 🛠 Функции

- Калькулятор басовых струн (одинарная/двойная навивка)
- Определение возраста фортепиано по серийному номеру
- База мензур
- Регулировочные параметры механики
- Личный кабинет с историей расчётов
- Telegram-бот с полным функционалом
- Админ-панель (веб + бот)

## Лицензия

MIT
