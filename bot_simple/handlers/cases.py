from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import urllib.request, urllib.parse, json

from app.config import config


class CasesHandler:
    def __init__(self):
        self.api_base = "http://backend:8000/api/v1"

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поиск кейсов по симптому"""
        if not context.args:
            await update.message.reply_text(
                "🔍 Использование: /search <симптом>\n\n"
                "Пример: /search глухой звук в теноре"
            )
            return

        query = " ".join(context.args)
        
        try:
            # Пока простой поиск через API (позже добавим RAG)
            response = urllib.request.urlopen(f"{self.api_base}/cases/?limit=5")
            data = json.loads(response.read())
            cases = data
            
            # Фильтруем по запросу (простой поиск в тексте)
            matched = [
                c for c in cases 
                if query.lower() in c['symptom'].lower() or query.lower() in c['title'].lower()
            ]
            
            if not matched:
                await update.message.reply_text("❌ Кейсы не найдены. Попробуйте другой запрос.")
                return
            
            for case in matched[:3]:
                keyboard = [[InlineKeyboardButton("📖 Читать полностью", url=f"http://localhost:3000/cases/{case['id']}")]]
                await update.message.reply_text(
                    f"📚 *{case['title']}*\n\n"
                    f"🔍 {case['symptom'][:100]}...\n\n"
                    f"Сложность: {case['difficulty']}\n"
                    f"Теги: {', '.join(case['tags']) if case['tags'] else 'нет'}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка поиска: {str(e)}")

    async def add_case_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Визард добавления кейса"""
        await update.message.reply_text(
            "➕ *Добавление нового кейса*\n\n"
            "Эта функция пока доступна только через веб-интерфейс:\n"
            "http://localhost:3000/cases/new\n\n"
            "В будущем будет полный визард здесь!",
            parse_mode="Markdown"
        )


    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inline-режим: поиск кейсов прямо в чате через @bot"""
        query = update.inline_query.query.strip()
        
        if not query or len(query) < 2:
            await update.inline_query.answer([], cache_time=1)
            return
        
        try:
            import urllib.request, urllib.parse, json
            url = f"http://backend:8000/api/v1/ai/search?{urllib.parse.urlencode({'q': query})}"
            resp = urllib.request.urlopen(url, timeout=5)
            data = json.loads(resp.read())
            results = data.get("results", [])
        except Exception:
            results = []
        
        from telegram import InlineQueryResultArticle, InputTextMessageContent
        
        articles = []
        for r in results[:10]:
            text = f"🔧 {r['title']}\n\n💡 {r['symptom']}\n\n✅ Решение: см. кейс #{r['case_id']}"
            articles.append(
                InlineQueryResultArticle(
                    id=str(r["case_id"]),
                    title=r["title"],
                    description=f"{r['symptom'][:60]}... (score: {r['score']})",
                    input_message_content=InputTextMessageContent(text),
                )
            )
        
        if not articles:
            articles.append(
                InlineQueryResultArticle(
                    id="no_results",
                    title="Ничего не найдено",
                    description=f"По запросу «{query}» нет результатов",
                    input_message_content=InputTextMessageContent(f"❌ По запросу «{query}» ничего не найдено"),
                )
            )
        
        await update.inline_query.answer(articles, cache_time=30)


    async def ai_assistant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI-ассистент: поиск через RAG + контекстный ответ"""
        if not context.args:
            await update.message.reply_text(
                "🤖 Использование: /ai <описание проблемы>\n\n"
                "Пример: /ai клавиша не возвращается после нажатия"
            )
            return

        query = " ".join(context.args)
        
        try:
            url = f"{self.api_base}/ai/search?{urllib.parse.urlencode({'q': query})}"
            resp = urllib.request.urlopen(url, timeout=10)
            data = json.loads(resp.read())
            results = data.get("results", [])
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка поиска: {e}")
            return
        
        if not results:
            await update.message.reply_text(
                f"🤷 По запросу «{query}» ничего не найдено.\n\n"
                "Попробуйте описать проблему другими словами или добавьте новый кейс через /add_case"
            )
            return
        
        # Формируем контекстный ответ
        response = f"🤖 **Найдено по запросу:** «{query}»\n\n"
        
        for i, r in enumerate(results[:3], 1):
            tags = ", ".join(r.get("tags", []))
            response += (
                f"**{i}. {r['title']}** (совпадение: {r['score']:.0%})\n"
                f"💡 Симптом: {r['symptom']}\n"
                f"🏷 Теги: {tags}\n"
                f"🔗 Кейс #{r['case_id']}\n\n"
            )
        
        response += "_Используйте /search для более точного поиска_"
        
        await update.message.reply_text(response, parse_mode="Markdown")
