from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
import urllib.request, urllib.parse, json

from app.config import config


class CasesHandler:
    def __init__(self):
        self.api_base = "http://backend:8000/api/v1"
        self.web_base = "http://localhost:3000"

    def _api_get(self, path: str) -> dict | list:
        """GET запрос к API"""
        url = f"{self.api_base}{path}"
        resp = urllib.request.urlopen(url, timeout=10)
        return json.loads(resp.read())

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поиск кейсов: /search <запрос>"""
        if not context.args:
            await update.message.reply_text(
                "🔍 *Поиск по базе знаний*\n\n"
                "Использование: `/search <симптом>`\n\n"
                "Примеры:\n"
                "• `/search клавиша западает`\n"
                "• `/search глухой звук`\n"
                "• `/search педаль не работает`",
                parse_mode="Markdown"
            )
            return

        query = " ".join(context.args)

        try:
            params = urllib.parse.urlencode({"search": query, "limit": 5})
            data = self._api_get(f"/cases/?{params}")
            items = data.get("items", []) if isinstance(data, dict) else data

            if not items:
                await update.message.reply_text(
                    f"❌ По запросу «{query}» ничего не найдено.\n\n"
                    "Попробуйте другие слова или добавьте кейс через веб: "
                    f"{self.web_base}/cases/new"
                )
                return

            for case in items[:5]:
                symptoms = ", ".join(s["name"] for s in case.get("symptoms", []))
                tags = ", ".join(t["name"] for t in case.get("tags", []))
                solutions_count = case.get("solutions_count", 0)

                text = (
                    f"📚 *{case['title']}*\n\n"
                    f"🔍 {case.get('symptom_text', '')[:150]}\n"
                )
                if symptoms:
                    text += f"🔧 Симптомы: {symptoms}\n"
                if tags:
                    text += f"🏷 Теги: {tags}\n"
                text += f"💡 Решений: {solutions_count}\n"
                diff = {"easy": "🟢 Легко", "medium": "🟡 Средне", "hard": "🔴 Сложно"}
                text += f"⚙️ {diff.get(case.get('difficulty', ''), case.get('difficulty', ''))}"

                keyboard = [[InlineKeyboardButton(
                    "📖 Читать полностью",
                    url=f"{self.web_base}/cases/{case['id']}"
                )]]

                await update.message.reply_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка поиска: {str(e)}")

    async def add_case_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление кейса — перенаправление на веб"""
        keyboard = [[InlineKeyboardButton(
            "➕ Добавить кейс через веб",
            url=f"{self.web_base}/cases/new"
        )]]
        await update.message.reply_text(
            "➕ *Добавление нового кейса*\n\n"
            "Для удобного создания кейса с выбором симптомов, тегов и загрузкой фото "
            "используйте веб-интерфейс:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inline-режим: @bot <запрос> — поиск кейсов в любом чате"""
        query = update.inline_query.query.strip()

        if not query or len(query) < 2:
            await update.inline_query.answer([], cache_time=1)
            return

        try:
            # Сначала пробуем обычный поиск
            params = urllib.parse.urlencode({"search": query, "limit": 10})
            data = self._api_get(f"/cases/?{params}")
            items = data.get("items", []) if isinstance(data, dict) else data
        except Exception:
            items = []

        articles = []
        for case in items[:10]:
            symptom_text = case.get("symptom_text", "")[:80]
            symptoms = ", ".join(s["name"] for s in case.get("symptoms", []))
            description = symptom_text or symptoms or "Нет описания"

            full_text = (
                f"📚 *{case['title']}*\n\n"
                f"🔍 {case.get('symptom_text', '')}\n"
            )
            if symptoms:
                full_text += f"🔧 {symptoms}\n"
            full_text += f"\n🔗 {self.web_base}/cases/{case['id']}"

            articles.append(InlineQueryResultArticle(
                id=str(case["id"]),
                title=case["title"],
                description=description,
                input_message_content=InputTextMessageContent(
                    full_text, parse_mode="Markdown"
                ),
                url=f"{self.web_base}/cases/{case['id']}",
            ))

        if not articles:
            articles.append(InlineQueryResultArticle(
                id="no_results",
                title="Ничего не найдено",
                description=f"По запросу «{query}» нет результатов",
                input_message_content=InputTextMessageContent(
                    f"❌ По запросу «{query}» ничего не найдено"
                ),
            ))

        await update.inline_query.answer(articles, cache_time=30)

    async def ai_assistant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI-ассистент (пока fallback на обычный поиск)"""
        if not context.args:
            await update.message.reply_text(
                "🤖 *AI-ассистент*\n\n"
                "Опишите проблему, и я найду подходящие кейсы:\n"
                "`/ai клавиша не возвращается после нажатия`\n\n"
                "_Скоро здесь будет умный RAG-поиск!_",
                parse_mode="Markdown"
            )
            return

        # Пока используем обычный поиск как fallback
        query = " ".join(context.args)
        try:
            params = urllib.parse.urlencode({"search": query, "limit": 3})
            data = self._api_get(f"/cases/?{params}")
            items = data.get("items", []) if isinstance(data, dict) else data
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
            return

        if not items:
            await update.message.reply_text(
                f"🤷 По запросу «{query}» ничего не найдено.\n\n"
                "Попробуйте описать проблему другими словами."
            )
            return

        response = f"🤖 *Найдено по запросу:* «{query}»\n\n"
        for i, case in enumerate(items[:3], 1):
            symptoms = ", ".join(s["name"] for s in case.get("symptoms", []))
            response += (
                f"*{i}. {case['title']}*\n"
                f"🔍 {case.get('symptom_text', '')[:100]}\n"
            )
            if symptoms:
                response += f"🔧 {symptoms}\n"
            response += f"🔗 {self.web_base}/cases/{case['id']}\n\n"

        await update.message.reply_text(response, parse_mode="Markdown")
