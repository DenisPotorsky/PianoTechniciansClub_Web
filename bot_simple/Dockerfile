FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir python-telegram-bot sqlalchemy python-dotenv loguru unidecode

COPY . .

CMD ["python", "main.py"]
